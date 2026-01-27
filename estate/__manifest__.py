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
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
    ],
    #data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
}