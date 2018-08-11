# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PaymentReport(models.AbstractModel):
    _name = 'report.bi_payment_report.account_payment_template'

    @api.model
    def render_html(self, docids, data):
        grouped_dict = {}
        date_from = data['date_from']
        date_to = data['date_to']
        payment_objects = self.env['account.payment'].browse(data['ids'])
        # group payment {'date': {'date':payment_date, 'team':sale_team_id,'journal':journal_id,'records':[ gruoped records]},....}
        for payment in payment_objects:
            if payment.sale_team_id:
                date = payment.payment_date
                if date in grouped_dict:
                    # team in same date dictionary
                    if payment.sale_team_id.name in grouped_dict[date].keys():
                        # journal in team dictionary keys
                        if payment.journal_id.name in grouped_dict[date][payment.sale_team_id.name].keys():
                            grouped_dict[date][payment.sale_team_id.name][payment.journal_id.name]['records'].append(payment)

                        else:
                            grouped_dict[date][payment.sale_team_id.name].update(
                                {payment.journal_id.name: {'records': [payment]}})


                    # team not in same date dictionary
                    else:
                        grouped_dict[date].update(
                            {payment.sale_team_id.name: {payment.journal_id.name: {'records': [payment]}}})
                # add new payment date
                else:
                    grouped_dict[date] = {payment.sale_team_id.name: {payment.journal_id.name: {'records': [payment]}}}

        docs = {
            'doc_model': 'account.payment',
            'docs': grouped_dict,
            'dates': [date_from, date_to]

        }
        print("grouped_dict", grouped_dict)
        return self.env['report'].render('bi_payment_report.account_payment_template', docs)


class PaymentReportWizard(models.TransientModel):
    _name = 'payment.report.wizard'

    date_from = fields.Date(string='From', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To', required=True, default=fields.Date.context_today)
    select_all_records = fields.Boolean(string='Select All')
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   domain=[('type', 'in', ('cash', 'bank'))])
    team_ids = fields.Many2many('crm.team', string='Sales Team', required=True)

    @api.onchange('select_all_records')
    def get_journal_and_teams(self):
        for rec in self:
            if rec.select_all_records:
                rec.journal_ids = self.env['account.journal'].search([('type', 'in', ('cash', 'bank'))]).ids
                rec.team_ids = self.env['crm.team'].search([]).ids

    @api.multi
    def print_payment_report(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(_('Date from must be less than date to'))

        search_domain = [('payment_date', '>=', rec.date_from), ('payment_date', '<=', rec.date_to),
                         ('payment_type', '=', 'inbound'),
                         ('sale_team_id', 'in', rec.team_ids.ids), ('journal_id', 'in', rec.journal_ids.ids)]
        payment_objects = self.env['account.payment'].search(search_domain)

        data = {
            'ids': payment_objects.ids,
            'date_from': rec.date_from,
            'date_to': rec.date_to,
        }
        return self.env['report'].get_action(self, 'bi_payment_report.account_payment_template', data=data)
