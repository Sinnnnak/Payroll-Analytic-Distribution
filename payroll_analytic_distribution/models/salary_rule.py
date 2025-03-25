# -*- coding: utf-8 -*-
from odoo import models, fields


class SalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    is_work_entry_calc = fields.Boolean(
        string='Work Entry Calculation',
        default=False,
        help="If enabled, this rule will be calculated based on work entry details"
    )