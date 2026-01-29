from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Name", required=True)
    
    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The name must be unique.',
    )
