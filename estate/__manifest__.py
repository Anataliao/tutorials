{
    'name': "Real Estate",
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
        'security/ir.model.access.cvs',
    ],
    #data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
}