#-*- coding:utf-8 -*-
import json
from collections import defaultdict
from markupsafe import Markup
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, plaintext2html
from datetime import datetime, time

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for slip in self:
            if slip.struct_id.is_use_work_entry_based_computation == True:
                new_lines = []
                move_dict = {
                        'narration': '',
                        'ref': fields.Date().end_of(slip.date_to, 'month').strftime('%B %Y'),
                        'journal_id': slip.struct_id.journal_id.id,
                        'date': slip.date_to,
                    }
                date_to = slip.date_to + relativedelta(day=1, month=slip.date_to.month + 1)
                work_entries = self.env['hr.work.entry'].search([
                    ('employee_id', '=', slip.employee_id.id),
                    ('state', '=', 'validated')
                ])

                filtered_work_entries = []
                for work_entry in work_entries:
                    date_start = work_entry.date_start.date() + relativedelta(days=1)
                    date_stop = work_entry.date_stop.date()
                    if slip.date_from <= date_start <= date_to and slip.date_from <= date_stop <= date_to:
                        filtered_work_entries.append(work_entry)

                grouped_work_entries = {}
                for work_entry in filtered_work_entries:
                    analytic_distribution_str = json.dumps(work_entry.analytic_distribution, sort_keys=True)
                    if analytic_distribution_str not in grouped_work_entries:
                        grouped_work_entries[analytic_distribution_str] = []
                        grouped_work_entries[analytic_distribution_str].append(work_entry)


                for analytic_distribution, work_entries_group in grouped_work_entries.items():
                    contract = slip.contract_id
                    for line in work_entries_group:
                        total_hours = line.duration
                        working_hours_per_month = contract.resource_calendar_id.hours_per_day * fields.Date().end_of(slip.date_from, 'month').day
                        hourly_rate = contract.wage / working_hours_per_month if working_hours_per_month else 0.0
                        basic_salary = total_hours * hourly_rate
                        for net in slip.line_ids:
                            if net.code == 'NET':
                                net_amount = net.total
                                net_without_wage  = net_amount - contract.wage
                                net_for_salary_work_entry = net_without_wage + basic_salary

                                net_debit_line = {
                                        'name': f'NET FOR: {line.name}',
                                        'partner_id': slip.employee_id.work_contact_id.id,
                                        'account_id': net.salary_rule_id.account_debit.id,
                                        'journal_id': slip.struct_id.journal_id.id,
                                        'date': slip.date,
                                        'debit': net_for_salary_work_entry if net_for_salary_work_entry > 0 else 0.0,
                                        'credit': -net_for_salary_work_entry if net_for_salary_work_entry < 0 else 0.0,
                                        'analytic_distribution': line.analytic_distribution,
                                    }
                                new_lines.append(net_debit_line)

                                net_credit_line = {
                                    'name': f'Net FOR: {line.name}',
                                    'partner_id': slip.employee_id.work_contact_id.id,
                                    'account_id': net.salary_rule_id.account_credit.id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': slip.date,
                                    'debit': -net_for_salary_work_entry if net_for_salary_work_entry < 0 else 0.0,
                                    'credit': net_for_salary_work_entry if net_for_salary_work_entry > 0 else 0.0,
                                    'analytic_distribution': line.analytic_distribution,
                                }
                                new_lines.append(net_credit_line)

                            if net.code == 'BASIC':
                                debit_line = {
                                    'name': f'BASIC FOR: {line.name}',
                                    'partner_id': slip.employee_id.work_contact_id.id,
                                    'account_id': net.salary_rule_id.account_debit.id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': slip.date,
                                    'debit': basic_salary if basic_salary > 0 else 0.0,
                                    'credit': -basic_salary if basic_salary < 0 else 0.0,
                                    'analytic_distribution': line.analytic_distribution,
                                }
                                new_lines.append(debit_line)

                                # Create credit entry
                                credit_line = {
                                    'name': f'BASIC FOR: {line.name}',
                                    'partner_id': slip.employee_id.work_contact_id.id,
                                    'account_id': net.salary_rule_id.account_credit.id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': slip.date,
                                    'debit': -basic_salary if basic_salary < 0 else 0.0,
                                    'credit': basic_salary if basic_salary > 0 else 0.0,
                                    'analytic_distribution': line.analytic_distribution,
                                }
                                new_lines.append(credit_line)

                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in new_lines]  
                move = self._create_account_move(move_dict)
                slip.write({'move_id': move.id})

            else:
                super(HrPayslip, slip)._action_create_account_move()
