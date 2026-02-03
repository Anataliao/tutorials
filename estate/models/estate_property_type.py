from odoo import models, fields
from odoo import api, fields, models 


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "name"


    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer()

    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The name must be unique.',
    )

    property_ids = fields.One2many(
        'estate.property',
        'property_type_id',
        string='Properties'
    )

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_type_id"
    )

    offer_count = fields.Integer(
        compute="_compute_offer_count"
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)