from odoo import api, fields, models
from odoo.fields import Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        res = super().action_sold()

        for record in self:
            record.env['account.move'].create({
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    Command.create({
                        'name': 'Comisión inmobiliaria (6%)',
                        'quantity': 1,
                        'price_unit': record.selling_price * 0.06,
                    }),
                    Command.create({
                        'name': 'Gastos administrativos',
                        'quantity': 1,
                        'price_unit': 100.0,
                    })
                ]
            })

        return res
