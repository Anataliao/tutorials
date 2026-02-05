from odoo import models, fields
from datetime import timedelta
from odoo import api, fields, models 
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = "price desc"

    price = fields.Float(
        string="Price"
    
    )

    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        string="Status",
        copy=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
        ondelete='cascade'
    )

    property_type_id = fields.Many2one(
        "estate.property.type",
        related="property_id.property_type_id",
        store=True,
        string="Property Type"
    )

    validity= fields.Integer(
        default=7
    )

    date_deadline= fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",

    )
   
    _check_price = models.Constraint(
        'CHECK(price > 0)',
        'The offer price must be strictly positive.',
    )

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            property_rec = self.env['estate.property'].browse(vals.get('property_id'))

            if property_rec.offer_ids:
                max_price = max(property_rec.offer_ids.mapped('price'))
                if vals.get('price') < max_price:
                    raise UserError(
                        "You cannot create an offer lower than an existing offer."
                    )

            property_rec.state = 'offer_received'

        return super().create(vals_list)

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = None

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date.date() and record.date_deadline:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days


    def action_accept(self):
        for offer in self:
            offer.status = 'accepted' 
            offer.property_id.state = 'offer_accepted'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price 

    def action_refuse(self):
        for offer in self:
            offer.status = 'refused'

    
