# -*- coding: utf-8 -*-
{
    'name': "Real Estate - Mod Cons",

    'summary': """
        Add Mod Cons on Property
    """,

    'description': """Mod Cons on Property""",

    'author': "GrowIT",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'real_estate'],

    'data': [
        'security/ir.model.access.csv',
        'data/real.estate.mod.cons.csv',
        'data/real.estate.project.mod.cons.csv',
        'views/views.xml',
        'views/res_config_settings.xml',
    ],
    'qweb': [
        "static/src/xml/widget.xml"
    ],
 
}