from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpenAcademyProgram(models.Model):
    _name = 'open.academy.program'
    _description = 'Academic Program'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string="Program Name",
        required=True
    )
    
    sequence = fields.Integer()

    code = fields.Char(
        string="Program Code",
        required=True
    )

    degree_title = fields.Char(
        string="Degree Title",
        required=True
    )

    director_id = fields.Many2one(
        'res.users',
        string="Program Director",
        required=True,
        domain=lambda self: [('group_ids', 'in', [self.env.ref('open_academy.group_coordination').id])]
    )

    active = fields.Boolean(
        default=True
    )

    subject_ids = fields.One2many(
        'open.academy.subject',
        'program_id',
        string="Subjects"
    )

    total_credits = fields.Integer(
        string="Total Credits",
        compute="_compute_total_credits",
        store=True
    )

    registration_ids = fields.One2many(
        'open.academy.registration',
        'program_id',
        string="Registrations"
    )

    registration_count = fields.Integer (
        string='Registrations',
        compute="_compute_registration_count",
        store=True
    )

    @api.depends('registration_ids')
    def _compute_registration_count(self):
        for rec in self:
            rec.registration_count = len(rec.registration_ids.filtered(lambda r: r.active))

    def action_view_registrations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrations',
            'view_mode': 'list,form',
            'res_model': 'open.academy.registration',
            'domain': [('program_id', '=', self.id)],
        }

    # Calcular total créditos automáticamente
    @api.depends('subject_ids.number_credits')
    def _compute_total_credits(self):
        for rec in self:
            rec.total_credits = sum(
                rec.subject_ids.mapped('number_credits')
            )

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'The program code must be unique.'
    )
