from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, date

class EduSession(models.Model):
    _name = 'edu.session'
    _description = 'Lớp học'

    name = fields.Char(string='Tên lớp', required=True)
    code = fields.Char(string='Mã lớp', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Dự thảo'),
        ('open', 'Mở đăng ký'),
        ('done', 'Kết thúc'),
        ('cancel', 'Hủy')
    ], string='Trạng thái', default='draft', required=True)
    
    start_date = fields.Date(string='Ngày bắt đầu', required=True)
    duration = fields.Float(string='Thời lượng (ngày)', default=1.0)
    end_date = fields.Date(string='Ngày kết thúc', compute='_compute_end_date', store=True)
    seats = fields.Integer(string='Số ghế', default=10)
    taken_seats = fields.Float(string='% Đã đăng ký', compute='_compute_taken_seats', store=True)
    
    course_id = fields.Many2one('edu.course', string='Khóa học', required=True)
    instructor_id = fields.Many2one('res.partner', string='Giảng viên', 
                                    domain=[('is_instructor', '=', True)])
    classroom_id = fields.Many2one('edu.classroom', string='Phòng học')
    attendee_ids = fields.Many2many('res.partner', string='Học viên')
    product_id = fields.Many2one('product.template', string='Học phí', 
                                  domain=[('is_edu_fee', '=', True)])
    revenue = fields.Monetary(string='Doanh thu', compute='_compute_revenue', store=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', 
                                   default=lambda self: self.env.company.currency_id)
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('edu.session') or 'New'
        return super(EduSession, self).create(vals)
    
    @api.model
    def default_get(self, fields_list):
        res = super(EduSession, self).default_get(fields_list)
        if 'start_date' in fields_list:
            res['start_date'] = date.today() + timedelta(days=1)
        return res
    
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for session in self:
            if session.start_date and session.duration:
                session.end_date = session.start_date + timedelta(days=session.duration)
            else:
                session.end_date = session.start_date
    
    @api.depends('seats', 'attendee_ids')
    def _compute_taken_seats(self):
        for session in self:
            if session.seats > 0:
                session.taken_seats = (len(session.attendee_ids) / session.seats) * 100
            else:
                session.taken_seats = 0.0
    
    @api.depends('attendee_ids', 'product_id')
    def _compute_revenue(self):
        for session in self:
            if session.product_id and session.attendee_ids:
                session.revenue = len(session.attendee_ids) * session.product_id.list_price
            else:
                session.revenue = 0.0
    
    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id and self.course_id.responsible_id:
            partners = self.env['res.partner'].search([
                ('user_ids', 'in', self.course_id.responsible_id.id),
                ('is_instructor', '=', True)
            ], limit=1)
            if partners:
                self.instructor_id = partners[0]
    
    @api.onchange('seats')
    def _onchange_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': 'Cảnh báo',
                    'message': 'Số ghế không thể âm!'
                },
                'value': {'seats': 0}
            }
    
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for session in self:
            if session.instructor_id and session.instructor_id in session.attendee_ids:
                raise ValidationError('Giảng viên không thể là học viên của chính lớp mình dạy!')
    
    @api.constrains('duration')
    def _check_duration(self):
        for session in self:
            if session.duration <= 0:
                raise ValidationError('Thời lượng khóa học phải lớn hơn 0!')
    
    @api.constrains('classroom_id', 'start_date', 'end_date')
    def _check_room_overlap(self):
        for session in self:
            if session.classroom_id and session.start_date and session.end_date:
                overlapping = self.search([
                    ('id', '!=', session.id),
                    ('classroom_id', '=', session.classroom_id.id),
                    ('start_date', '<=', session.end_date),
                    ('end_date', '>=', session.start_date),
                    ('state', 'not in', ['cancel'])
                ])
                if overlapping:
                    raise ValidationError(
                        f'Phòng {session.classroom_id.name} đã được sử dụng trong khoảng thời gian này!'
                    )
    
    def action_open(self):
        for session in self:
            if not session.classroom_id or not session.instructor_id:
                raise UserError('Phải có phòng học và giảng viên mới có thể mở lớp!')
            session.state = 'open'
    
    def action_done(self):
        self.write({'state': 'done'})
    
    def action_cancel(self):
        for session in self:
            if session.state == 'done':
                raise UserError('Không thể hủy lớp đã kết thúc!')
            session.state = 'cancel'
    
    def unlink(self):
        for session in self:
            if session.state not in ('draft', 'cancel'):
                raise UserError('Chỉ có thể xóa lớp ở trạng thái Dự thảo hoặc Hủy!')
        return super(EduSession, self).unlink()
    
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'state': 'draft',
            'attendee_ids': [],
        })
        return super(EduSession, self).copy(default)
    
    def name_get(self):
        result = []
        for session in self:
            name = f'[{session.code}] {session.name}'
            if session.start_date:
                name += f' - {session.start_date}'
            result.append((session.id, name))
        return result
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', 
                      ('code', operator, name),
                      ('name', operator, name),
                      ('instructor_id.name', operator, name)]
        sessions = self.search(domain + args, limit=limit)
        return sessions.name_get()
    
    def action_reset_draft(self):
        self.write({'state': 'draft'})
