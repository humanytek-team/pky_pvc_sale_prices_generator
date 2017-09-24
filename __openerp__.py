# -*- coding: utf-8 -*-
{
    'name': "Generate sale prices for PVC",
    'summary': """
        Adds a wizard that allow generate new prices based on parameters
        asociated to the operations of the company.""",
    'description': """
        Extension of addon sale for add a wizard that allow generate new
        prices based on parameters asociated to the operations of the
        company.
    """,
    'author': "Humanytek",
    'website': "http://www.humanytek.com",
    'category': 'Sales Management',
    'version': '1.0.0',
    'depends': ['sale', ],
    'data': [
        'views/pky_pvc_preformed_view.xml',
        'wizard/sale_prices_generator_view.xml',
    ],
    'demo': [
        'data/pky.pvc.preformed.csv',
    ],
}
