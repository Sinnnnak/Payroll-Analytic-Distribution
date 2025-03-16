#-*- coding:utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, plaintext2html

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    
    is_use_work_entry_based_computation = fields.Boolean(
        string="Use Work Entry Based Computation",
        default=False,
        help="When checked, salary computation will be calculated based on work entries."
    )
