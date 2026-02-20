from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpenAcademyRegistration(models.Model):
    _name = 'open.academy.registration'
    _description = 'Program Registration'
    _order = 'student_id'
    _rec_name = 'name'

    name = fields.Char(
        compute="_compute_name",
        store=True
)


    student_id = fields.Many2one(
        'open.academy.student',
        string="Student",
        required=True,
        ondelete="cascade"
    )

    program_id = fields.Many2one(
        'open.academy.program',
        string="Program",
        required=True,
        ondelete="cascade"
    )

    current_semester = fields.Selection(
        [(str(i), str(i)) for i in range(1, 11)],
        string="Current Semester",
        required=True
    )

    active = fields.Boolean(
        default=True
    )

    enrolment_ids = fields.One2many(
        'open.academy.enrolment',
        'registration_id',
        string="Enrolments"
    )

    semester_cost = fields.Float(
        string="Semester Cost",
        compute="_compute_semester_cost",
        store=True
    )

    insurance_value = fields.Float(
        string="Insurance",
        default=34000.0
    )

    total_to_pay = fields.Float(
        string="Total to Pay",
        compute="_compute_total_to_pay",
        store=True
    )

    # Calcular costo del semestre (materias inscritas)
    @api.depends('enrolment_ids.subject_id.cost_subject')
    def _compute_semester_cost(self):
        for rec in self:
            rec.semester_cost = sum(
                rec.enrolment_ids.mapped('subject_id.cost_subject')
            )
    
    @api.depends('student_id', 'program_id', 'current_semester')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.student_id.name} - {rec.program_id.name} (Sem {rec.current_semester})"

    # Calcular total a pagar (materias + seguro)
    @api.depends('semester_cost', 'insurance_value')
    def _compute_total_to_pay(self):
        for rec in self:
            rec.total_to_pay = rec.semester_cost + rec.insurance_value

    # No permitir 2 matrículas activas del mismo programa
    _unique_active_program = models.Constraint(
        'UNIQUE(student_id, program_id, active)',
        'The student already has an active registration for this program.'
    )
