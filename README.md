# stock_invoice_reversal

Generic Odoo 16 module that links `stock.picking` records to `account.move`
(invoices) and automates stock return on credit note creation.

## What it does

- Adds `picking_ids` Many2many on `account.move`
- On invoice **posting**: validates all linked pickings (consumes stock)
- On **credit note** creation: creates a draft return picking for each
  linked picking — warehouse operator confirms it manually

## Usage

Any module that creates an invoice from a warehouse operation simply sets
`picking_ids` at invoice creation time:

```python
invoice = self.env['account.move'].create({
    'move_type': 'out_invoice',
    'partner_id': partner.id,
    'picking_ids': [(4, picking.id)],
    # ... other fields
})
```

No further configuration needed.

## Dependencies

- `account` (Odoo standard)
- `stock` (Odoo standard)

## License

OPL-1 — © 2026 Boris Kumpar
