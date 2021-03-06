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
                    grouped_dict[date]['date_amount'] += payment.amount
                    if payment.sale_team_id.name in grouped_dict[date].keys():
                        grouped_dict[date][payment.sale_team_id.name]['team_amount'] += payment.amount
                        # journal in team dictionary keys
                        if payment.journal_id.name in grouped_dict[date][payment.sale_team_id.name].keys():
                            grouped_dict[date][payment.sale_team_id.name][payment.journal_id.name]['records'].append(
                                payment)
                            grouped_dict[date][payment.sale_team_id.name][payment.journal_id.name]['journal_amount'] += payment.amount

                        else:
                            grouped_dict[date][payment.sale_team_id.name].update(
                                {payment.journal_id.name: {'journal_amount': payment.amount,'records': [payment]}})


                    # team not in same date dictionary
                    else:
                        grouped_dict[date].update(
                            {payment.sale_team_id.name: {'team_amount': payment.amount,
                                                         payment.journal_id.name: {'journal_amount': payment.amount,
                                                                                   'records': [payment]}}})
                # add new payment date
                else:
                    grouped_dict[date] = {'date_amount': payment.amount,
                                          payment.sale_team_id.name: {'team_amount': payment.amount,
                                                                      payment.journal_id.name: {
                                                                          'journal_amount': payment.amount,
                                                                          'records': [payment]}}}

        docs = {
            'doc_model': 'account.payment',
            'docs': grouped_dict,
            'dates': [date_from, date_to]

        }
        return self.env['report'].render('bi_payment_report.account_payment_template', docs)


class PaymentReportWizard(models.TransientModel):
    _name = 'payment.report.wizard'

    @api.model
    def get_journals(self):
        current_user = self.env['res.users'].sudo().browse(self._uid)
        team_journal_ids = []
        if current_user:
            if current_user.has_group('account.group_account_manager'):
                journal_ids = self.env['account.journal'].sudo().search([('type', 'in', ('cash', 'bank'))]).ids
                return [('id', 'in', journal_ids)]
            else:
                sale_teams = self.env['crm.team'].sudo().search([])
                corporate_journal_id = self.env['account.journal'].sudo().search(
                    [('type', 'in', ('cash', 'bank')), ('is_corporate', '=', True)], limit=1).id
                if corporate_journal_id:
                    team_journal_ids.append(corporate_journal_id)
                for team in sale_teams:
                    for member in team.member_ids:
                        if member == current_user:
                            if team.cash_journal_id.id and team.cash_journal_id.id not in team_journal_ids:
                                team_journal_ids.append(team.cash_journal_id.id)
                            if team.bank_journal_id.id and team.bank_journal_id.id not in team_journal_ids:
                                team_journal_ids.append(team.bank_journal_id.id)
                            if team.bank_journal_id2.id and team.bank_journal_id2.id not in team_journal_ids:
                                team_journal_ids.append(team.bank_journal_id2.id)
                return [('id', 'in', team_journal_ids)]

    def get_teams(self):
        current_user = self.env['res.users'].sudo().browse(self._uid)
        if current_user:
            if current_user.has_group('account.group_account_manager'):
                team_ids = self.env['crm.team'].sudo().search([]).ids
                return [('id', 'in', team_ids)]
            else:
                sale_teams = self.env['crm.team'].sudo().search([])
                for team in sale_teams:
                    for member in team.member_ids:
                        if member == current_user:
                            return [('id', '=', team.id)]

    date_from = fields.Date(string='From', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To', required=True, default=fields.Date.context_today)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, domain=get_journals, )
    team_ids = fields.Many2many('crm.team', string='Sales Team', domain=get_teams, required=True)

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
