from odoo import models, fields
from datetime import timedelta
from odoo import api, fields, models 
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'

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
            offer.property_id.buyer = offer.partner_id
            offer.property_id.selling_price = offer.price 

    def action_refuse(self):
        for offer in self:
            offer.status = 'refused'
            
