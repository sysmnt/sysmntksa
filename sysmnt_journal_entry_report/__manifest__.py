# -*- coding: utf-8 -*-
# Part of Sysmnt. See LICENSE file for full copyright and licensing details.
{
    'name': 'Print Journal Entry Report PDF (Arabic & English)',
    'version': '17.0.0.0',
    'category': 'Accounting',
    'license': 'OPL-1',
    'summary': 'Custom Journal Entry PDF Report',
    'description': 'Professional custom layout for journal entry reports.',
    'author': "SYSMNT",
    'website': "https://www.sysmnt.com",
    'depends': ['account'],
    "images": [
        'static/description/icon.png'
    ],
    'data': [
        'report/report_journal_entries.xml',
        'report/report_journal_entries_view.xml',
    ],
    'price': 12.50,
    'currency': 'USD',
    'installable': True,
    'application': False,
}
