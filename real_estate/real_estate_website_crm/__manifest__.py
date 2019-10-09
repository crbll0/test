# -*- coding: utf-8 -*-
{
    'name': "Real Estate - Website",

    'summary': """
        Add the Fearure to publish the property on the website.    
    """,

    'description': """
    """,

    'author': "GrowIT",
    'website': "",
    'category': 'Uncategorized',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'real_estate', 'real_estate_mod_cons', 'website', 'crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

}