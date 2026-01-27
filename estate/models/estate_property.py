from odoo import models, fields
from dateutil.relativedelta import relativedelta
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property"

    active = fields.Boolean(
        default=True
    )
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3)

    )
    expected_price = fields.Float(
        string="Expected Price"
        
    )
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False
        
    )
    bedrooms = fields.Integer(
        string="Bedrooms",
        default=2
    )
    living_area = fields.Integer(
        string="Living Area (sqm)"
        
    )
    facades = fields.Integer(
        string="Facades"
    
    )
    garage = fields.Boolean(
        string="Garage",
        default=False
    )
    garden = fields.Boolean(
        string="Garden"
    
    )
    garden_area = fields.Integer(
        string="Garden Area"
    
    )
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        required=True
        
    )

    state = fields.Selection(
        string="state",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        required=True,
        copy=False,
        default='new'

    )

    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type"
    )

    salesman = fields.Many2one(
        "res.users",
        string="Salesman",
        default=lambda self: self.env.user
    )

    buyer = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False
    )


    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Property Tag"
    )

    other_info = fields.Text(string="Other Info")

    offer_ids = fields.One2many(
        'estate.property.offer', 
        'property_id',            
        string="Offers"
    )

