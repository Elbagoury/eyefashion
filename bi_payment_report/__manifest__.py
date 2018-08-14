# -*- coding: utf-8 -*-
{
    'name': "BI Solutions Payment Report",
    'summary': "BI Solutions Payment Report",
    'description': """ 
            This module add payment report as pdf from payment.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account_accountant', 'eyefashion_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pi_payment_wizard_view.xml',
        'views/account_payment_inherit.xml',
        'reports/account_payment_report.xml',
        'views/menu_items_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
