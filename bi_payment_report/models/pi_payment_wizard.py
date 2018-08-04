# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PaymentReport(models.AbstractModel):
    _name = 'report.bi_payment_report.account_payment_template'

    @api.model
    def render_html(self, docids, data):
        grouped_dict = {}
        print ("hereeeeeeeeee")
        payment_objects = self.env['account.payment'].browse(data['ids'])
        # group payment {'date_team_journal': {'name':grouped_name ,'date':payment_date, 'team':sale_team_id,'journal':journal_id,'records':[ gruoped records]},....}
        for payment in payment_objects:
            if payment.sale_team_id:
                grouped_name = payment.payment_date + " - " + payment.sale_team_id.name + " - " + payment.journal_id.name
                if grouped_name in grouped_dict:
                    grouped_dict[grouped_name]['records'].append(payment)
                else:
                    grouped_dict[grouped_name] = {'name': grouped_name, 'date': payment.payment_date,
                                                  'team': payment.sale_team_id.name,
                                                  'journal': payment.journal_id.name,
                                                  'records': [payment]}
        docs = {
            'doc_model': 'account.payment',
            'docs': grouped_dict,

        }
        return self.env['report'].render('bi_payment_report.account_payment_template', docs)


class PaymentReportWizard(models.TransientModel):
    _name = 'payment.report.wizard'

    date_from = fields.Date(string='From', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To', required=True, default=fields.Date.context_today)
    select_all_records = fields.Boolean(string='Select All')
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    team_ids = fields.Many2many('crm.team', string='Sales Team', required=True)

    @api.onchange('select_all_records')
    def get_journal_and_teams(self):
        for rec in self:
            if rec.select_all_records:
                rec.journal_ids = self.env['account.journal'].search([]).ids
                rec.team_ids = self.env['crm.team'].search([]).ids

    @api.multi
    def print_payment_report(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(_('Date from must be less than date to'))

        search_domain = [('payment_date', '>=', rec.date_from), ('payment_date', '<=', rec.date_to),
                         ('sale_team_id', 'in', rec.team_ids.ids), ('journal_id', 'in', rec.journal_ids.ids)]
        payment_objects = self.env['account.payment'].search(search_domain)

        data = {
            'ids': payment_objects.ids,

        }
        return self.env['report'].get_action(self, 'bi_payment_report.account_payment_template', data=data)
