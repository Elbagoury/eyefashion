# -*- coding: utf-8 -*-
{
    'name': "BI Delivery Slip Report",
    'summary': "BI Delivery Slip Report",
    'description': """ 
            This module calculate the sum of quantities in delivery slip report.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base', 'stock'],
    'data': [
        'reports/delivery_slip_inherit_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
