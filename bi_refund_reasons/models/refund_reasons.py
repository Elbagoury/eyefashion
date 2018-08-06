from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval


class RefundReasons(models.Model):
    _name = 'refund.reason'

    name = fields.Char(string='Reason', required=True)


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    description = fields.Many2one('refund.reason', string='Reasons', required=True)

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super(AccountInvoiceRefund, self).compute_refund(mode='refund')
        for refund in self:
            if res['domain'][1][2]:
                created_invoice = self.env['account.invoice'].browse(res['domain'][1][2])
                if created_invoice:
                    created_invoice.write({'name': refund.description.name})
        return res
