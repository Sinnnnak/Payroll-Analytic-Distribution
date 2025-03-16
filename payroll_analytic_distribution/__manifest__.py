# -*- coding: utf-8 -*-
{
    'name': "Payroll Analytic Distribution",
    'summary': """
        Distribute payroll costs based on work entries""",
    'description': """
        This module allows distributing payroll costs based on employee attendance
        and work entries with analytic accounts.
    """,
    'author': "Mohamed Elmojtaba",
    'category': 'Human Resources/Payroll',
    'version': '1.0',
    'depends': ['hr_payroll', 'hr_work_entry', 'analytic','hr_payroll_account'],
    'data': [
        'views/hr_work_entry.xml',
        'views/salary_structure.xml',
    ],
}
