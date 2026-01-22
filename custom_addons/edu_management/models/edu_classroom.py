from odoo import models, fields

class EduClassroom(models.Model):
    _name = 'edu.classroom'
    _description = 'Phòng học'

    name = fields.Char(string='Tên phòng', required=True)
    capacity = fields.Integer(string='Sức chứa tối đa', default=30)
