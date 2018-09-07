# -*- coding: utf-8 -*-
{
    'name': "BI Internal Transfer Filter",
    'summary': "BI Internal Transfer Filter",
    'description': """ 
            add filter on internal transfer.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Warehouse',
    'version': '0.1',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_picking_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
