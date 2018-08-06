# -*- coding: utf-8 -*-
{
    'name': "BI Solutions Payment Date",

    'summary': "BI Solutions Payment Date",

    'description': """
       This module will allow a group of users to edit payment date. 
    """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account_accountant'],
    'data': [
        'views/account_payment_inherit_view.xml',
    ],
    'sequence': 1
}
