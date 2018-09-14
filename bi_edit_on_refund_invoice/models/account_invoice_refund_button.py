# -*- coding: utf-8 -*-
from odoo import models, api, _ 
from odoo.exceptions import Warning

class editOnRefundInvoice(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def invoice_refund(self):
        curr_invoice_id = self._context.get('active_id')
        # print (curr_invoice_id)
        curr_invoice_obj = self.env['account.invoice'].browse(curr_invoice_id)
        refunded_invoices = self.env['account.invoice'].search([('refund_invoice_id', '=', curr_invoice_id)])
        # print (refunded_invoices)
        # print (curr_invoice_obj)
        for line in curr_invoice_obj.invoice_line_ids:
            # print (line.product_id.name)
            # print (line.quantity)
            for refunded_invoice in refunded_invoices:
                for refund_invoice_line in refunded_invoice.invoice_line_ids:
                    # print (refund_invoice_line.product_id.name)
                    if line.product_id == refund_invoice_line.product_id:
                        if line.quantity == refund_invoice_line.quantity:
                            raise Warning(_('You can not confirm refund invoice, it was already confirmed with similar quantity.'))
        return super(editOnRefundInvoice, self).invoice_refund()