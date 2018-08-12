# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_order_value = fields.Date(string='Sale Order Date', required=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                   default=fields.Date.context_today, )
