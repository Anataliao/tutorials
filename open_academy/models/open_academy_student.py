from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpenAcademyStudent(models.Model):
    _name = 'open.academy.student'
    _description = 'Student'

    name = fields.Char(related='user_id.name')

    sequence = fields.Integer()

    user_id = fields.Many2one(
        'res.users',
        string="Assigned Student",
        required=True,
        domain=lambda self: [('group_ids', 'in', [self.env.ref('open_academy.group_students').id])]
    )

    identification = fields.Char(
        string="Identification",
        required=True
    )

    email = fields.Char(
        string="Email",
        required=True
    )

    phone = fields.Char(
        string="Phone"
    )

    active = fields.Boolean(
        default=True
    )

    registration_ids = fields.One2many(
        'open.academy.registration',
        'student_id',
        string="Registrations"
    )

    enrolment_ids = fields.One2many(
        'open.academy.enrolment',
        'student_id',
        string="Enrolments"
    )

    average = fields.Float(
        string="Average Grade",
        compute="_compute_average",
        store=True
    )

    active_registrations = fields.Integer(
        string="Active Registrations",
        compute="_compute_active_registrations",
        store=True
    )

    # Calcular promedio por créditos
    @api.depends('enrolment_ids.grade_id.final_grade', 'enrolment_ids.credits')
    def _compute_average(self):
        for rec in self:
            total_weight = 0 #suma (nota * creditos)
            total_credits = 0 #suma total de creditos 

            for enrol in rec.enrolment_ids: # recorre todas las materias donde el est este inscrito
                if enrol.grade_id and enrol.grade_id.final_grade: # toma en cuenta las materias que tienen registro de nota y notaa final
                    total_weight += enrol.grade_id.final_grade * enrol.credits
                    total_credits += enrol.credits

            rec.average = (
                total_weight / total_credits
                if total_credits > 0 else 0.0
            )

    # Contar matrículas activas
    @api.depends('registration_ids.active')
    def _compute_active_registrations(self):
        for rec in self:
            rec.active_registrations = len(
                rec.registration_ids.filtered(lambda r: r.active)
            )

    # Máximo 2 matrículas activas
    @api.constrains('registration_ids')
    def _check_max_active_registrations(self):
        for rec in self:
            active_regs = rec.registration_ids.filtered(lambda r: r.active)
            if len(active_regs) > 2:
                raise ValidationError(
                    "A student can only have a maximum of 2 active registrations."
                )

    # Identificación única
    _unique_identification = models.Constraint(
        'UNIQUE(identification)',
        'The identification must be unique.'
    )
