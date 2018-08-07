# -*- coding: utf-8 -*-
{

    'name': "BI Solutions Refund Reasons",

    'summary': "BI Solutions Refund Reasons",

    'description': """
       This module add make refund text new model. 
    """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/refund_reasons_view.xml',
    ],
    'sequence': 1
}
