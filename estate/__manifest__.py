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
        'views/mymodule_view.xml',
    ],
    #data files containing optionally loaded demonstration data
    'demo': [
        'demo/demo_data.xml',
    ],
}