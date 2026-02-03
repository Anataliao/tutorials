from odoo import models, fields
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class EstateProperty(models.Model):

    _name = "estate.property"
    _description = "Property"
    _order = "id desc"

 
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
    
    total_area = fields.Float(
        string="Total Area (sqm)",
        compute="_compute_total_area",
        store=True
    )

    best_price = fields.Float(
        string= "Best Price",
        compute="_compute_best_price"
    )
    
 
    _check_expect= models.Constraint(
        'CHECK(expected_price > 0)',
        'A property expected price must be strictly positive.',
    )
    
    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'A property selling price must be positive.',
    )

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)
    
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0


    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue

            if float_compare(
                record.selling_price,
                record.expected_price * 0.9,
                precision_digits=2
            ) < 0:
                raise ValidationError(
                    "The selling price cannot be less than 90% of the expected price."
                )
    
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Una propiedad vendida no puede ser cancelada.")
            record.state = 'cancelled'
        return True

    def action_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("A cancelled property cannot be sold.")
            record.state = 'sold'
        return True

