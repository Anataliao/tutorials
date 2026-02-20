{
    'name': "Open Academy",
    'version': '1.0',
    'depends': ['base'],
    'author': "Natalia Ortiz",
    'category': 'apps',
    'description': """
    learning about odoo
    """,
    "application": True,

    # data files always loaded at installation
    'data': [
        'security/res_group_security.xml',
        'security/base_user_role_open_academy.xml',
        'security/ir.model.access.csv',
        'views/academy_program_views.xml',
        'views/academy_subject_views.xml',
        'views/academy_student_views.xml',
        'views/academy_registration_views.xml',
        'views/academy_enrolment_views.xml',
        'views/academy_grade_views.xml',
        'views/academy_menus.xml',
    ],
    #data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
}