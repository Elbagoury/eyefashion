# -*- coding: utf-8 -*-
{
    'name': "BI Edit on Refund Invoice Button",
    'summary': "BI edit on refund invoice button",
    'description': """ 
            This module disable refund invoice button if the employee want to confirm invoice on the same quantity.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base', 'account_accountant', 'sale'],
    'data': [
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
