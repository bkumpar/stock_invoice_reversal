# -*- coding: utf-8 -*-
# © 2026 Boris Kumpar. All rights reserved.
# License OPL-1 (https://www.odoo.com/documentation/user/licence.html)
{
    'name': 'Stock Invoice Reversal',
    'summary': 'Link stock pickings to invoices; auto-create return picking on credit note',
    'description': 'Adds a generic picking_ids Many2many on account.move. '
                   'On invoice posting: validates linked pickings. '
                   'On credit note: creates a draft return picking for manual confirmation.',
    'license': 'OPL-1',
    'author': 'Boris Kumpar',
    'website': 'https://github.com/bkumpar',
    'category': 'Inventory/Accounting',
    'version': '16.0.1.0.0',
    'depends': [
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
