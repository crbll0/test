# -*- coding: utf-8 -*-
{
    'name': "Real Estate",

    'summary': """
        
    """,

    'description': """
    """,

    'author': "GrowIT",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.2',

    'depends': ['base', 'account', 'report_py3o', 'crm'],

    'data': [
        'data/real.estate.property.type.csv',
        'data/product_data.xml',
        'data/sequence.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/views.xml',
        'views/pagos.xml',
        'views/inherit_crm.xml',
        'views/report_anexo_b_docier.xml',
        'views/report_quota_details.xml',
        'views/report_payment_recibo.xml',
        'views/report_cumplimiento.xml',
        'views/report_estado_cliente.xml',
        'views/report_py3o.xml',
        'views/report_quota_details.xml',
        'views/ir_config_settings.xml',
    ],
    'installable': True,
    'application': True,
}
