{
    'name': 'Estate Account',
    'summary': 'Automatic invoicing when selling a property',
    'description': 'Create an invoice when a property is marked as sold.',
    'author': 'My Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Real Estate',
    'version': '0.1',

    'depends': [
        'base',
        'estate',
        'account',
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

    'installable': True,
    'application': False,
}
