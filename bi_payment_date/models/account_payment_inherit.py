from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def get_default_user_access(self):
        user = self.env['res.users'].browse(self._uid)

        if user.has_group('account.group_account_manager'):
           return True
        else:
            return False

    check_user_access = fields.Boolean(string="Check User Access", default=get_default_user_access,
                                       compute='get_user_access')

    @api.multi
    def get_user_access(self):
        for rec in self:
            user = self.env['res.users'].browse(self._uid)
            if user.has_group('account.group_account_manager'):
                rec.check_user_access = True
            else:
                rec.check_user_access = False
