from odoo import models, fields, api

class EduCourse(models.Model):
    _name = 'edu.course'
    _description = 'Khóa học'

    name = fields.Char(string='Tên khóa học', required=True)
    description = fields.Html(string='Mô tả')
    active = fields.Boolean(string='Hoạt động', default=True)
    level = fields.Selection([
        ('basic', 'Cơ bản'),
        ('advanced', 'Nâng cao')
    ], string='Cấp độ', default='basic')
    
    responsible_id = fields.Many2one('res.users', string='Người phụ trách')
    subject_id = fields.Many2one('edu.subject', string='Môn học')
    session_ids = fields.One2many('edu.session', 'course_id', string='Các lớp học')
    session_count = fields.Integer(string='Số lớp', compute='_compute_session_count')
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tên khóa học phải duy nhất!')
    ]
    
    @api.onchange('responsible_id')
    def _onchange_responsible_id(self):
        if self.responsible_id and self.responsible_id.email:
            if not self.description:
                self.description = ''
            self.description += f'<p>Email người phụ trách: {self.responsible_id.email}</p>'
    
    @api.depends('session_ids')
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)
