# -*- coding: utf-8 -*-
# © 2026 Boris Kumpar. All rights reserved.
# License OPL-1 (https://www.odoo.com/documentation/user/licence.html)

from odoo import models, fields, _


class AccountMove(models.Model):
    """Extend account.move with a generic stock picking link.

    Any module that creates an invoice from a warehouse operation can set
    picking_ids to link the relevant stock.picking records.  This module
    then automatically:
      - validates linked pickings when the invoice is posted (confirmed)
      - creates a draft return picking for each linked picking when a
        credit note (reversal) is created — the warehouse operator must
        confirm the return picking manually after physically receiving
        the goods back.
    """

    _inherit = 'account.move'

    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='account_move_stock_picking_rel',
        column1='move_id',
        column2='picking_id',
        string='Stock Pickings',
        copy=False,
        readonly=True,
    )

    def _post(self, soft=True):
        """Validate linked stock pickings when the invoice is posted.

        Pickings are validated BEFORE super()._post() so that any stock
        error surfaces before the invoice is irrevocably posted.
        Quantity done is set to the reserved quantity to avoid the
        ImmediateTransferDetails wizard.
        """
        for move in self:
            for picking in move.picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel')
            ):
                for sm in picking.move_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')
                ):
                    sm.quantity_done = sm.product_uom_qty
                picking.with_context(
                    skip_backorder=True,
                    picking_ids_not_to_backorder=picking.ids,
                ).button_validate()
        return super()._post(soft=soft)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        """Create a draft return picking for each linked picking on reversal.

        The return picking is left in ready/draft state — the warehouse
        operator must confirm it after physically verifying the returned goods.
        """
        result = super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )
        for move in self:
            for picking in move.picking_ids.filtered(
                lambda p: p.state == 'done'
            ):
                return_moves = [
                    (0, 0, {
                        'product_id': sm.product_id.id,
                        'quantity': sm.product_uom_qty,
                        'move_id': sm.id,
                        'to_refund': True,
                    })
                    for sm in picking.move_ids.filtered(
                        lambda m: m.state == 'done'
                    )
                ]
                if not return_moves:
                    continue
                return_wizard = self.env['stock.return.picking'].with_context(
                    active_id=picking.id,
                    active_model='stock.picking',
                ).create({'product_return_moves': return_moves})
                new_picking_id, dummy = return_wizard._create_returns()
                new_picking = self.env['stock.picking'].browse(new_picking_id)
                new_picking.write({
                    'origin': _('Return: %s') % (picking.origin or picking.name),
                })
        return result
