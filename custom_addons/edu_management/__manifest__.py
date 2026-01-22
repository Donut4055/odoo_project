{
    'name': 'Educational Management',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Quản lý khóa học, lớp học và học viên',
    'description': """
        Module quản lý giáo dục bao gồm:
        - Quản lý khóa học và môn học
        - Quản lý lớp học và lịch học
        - Quản lý giảng viên và học viên
        - Báo cáo và phân tích
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'product'],
    'data': [
        'security/edu_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/edu_subject_views.xml',
        'views/edu_session_views.xml',
        'views/edu_course_views.xml',
        'views/edu_classroom_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/edu_menus.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
