# -*- coding: utf-8 -*-
{
    'name': "BI Count For Picking",
    'summary': "BI Count For Picking",
    'description': """ 
            This module add sum in initial demand page in picking,inventory,po,so and accounting.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base', 'stock', 'account_accountant', 'purchase', 'sale'],
    'data': [
        'views/count_for_picking.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
