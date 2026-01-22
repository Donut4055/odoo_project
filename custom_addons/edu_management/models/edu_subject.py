from odoo import models, fields, api

class EduSubject(models.Model):
    _name = 'edu.subject'
    _description = 'Môn học/Chuyên ngành'

    name = fields.Char(string='Tên môn học', required=True)
    code = fields.Char(string='Mã môn học')
    description = fields.Text(string='Mô tả')
    
    course_ids = fields.One2many('edu.course', 'subject_id', string='Các khóa học')
