# -*- coding: utf-8 -*-

from odoo import api, fields, models
import json

    
class HrWorkEntry(models.Model):
    _name = 'hr.work.entry'
    _inherit = ['hr.work.entry', 'analytic.mixin']
    
    
    analytic_distribution_text = fields.Text(company_dependent=True)
    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution", store=False, precompute=False)
    analytic_account_ids = fields.Many2many('account.analytic.account', compute="_compute_analytic_account_ids", copy=True)
    total_employee_hours = fields.Float(
        string='Total Employee Hours', 
        compute='_compute_total_employee_hours', 
        store=True,
        readonly=True,
        help="Total hours calculated by multiplying hours per day with duration")


    @api.depends('duration')
    def _compute_total_employee_hours(self):
        for record in self:
            record.total_employee_hours = record.duration * record.employee_id.resource_calendar_id.hours_per_day

    @api.depends_context('company')
    @api.depends('analytic_distribution_text')
    def _compute_analytic_distribution(self):
        for record in self:
            record.analytic_distribution = json.loads(record.analytic_distribution_text or '{}')

    def _inverse_analytic_distribution(self):
        for record in self:
            record.analytic_distribution_text = json.dumps(record.analytic_distribution)

    @api.depends('analytic_distribution')
    def _compute_analytic_account_ids(self):
        for record in self:
            record.analytic_account_ids = bool(record.analytic_distribution) and self.env['account.analytic.account'].browse(
                list({int(account_id) for ids in record.analytic_distribution for account_id in ids.split(",")})
            ).exists()