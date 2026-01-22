from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_instructor = fields.Boolean(string='Là giảng viên', default=False)
    session_teaching_ids = fields.One2many('edu.session', 'instructor_id', string='Lớp đang dạy')
    session_attending_ids = fields.Many2many('edu.session', string='Lớp đang học')
    session_count = fields.Integer(string='Số lớp dạy', compute='_compute_session_count')
    
    @api.depends('session_teaching_ids')
    def _compute_session_count(self):
        for partner in self:
            partner.session_count = len(partner.session_teaching_ids)
