from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpenAcademySubject(models.Model):
    _name = 'open.academy.subject'
    _description = 'Academic Subject'
    _order = 'semester, name'

    name = fields.Char(
        string="Subject Name",
        required=True
    )

    program_id = fields.Many2one(
        'open.academy.program',
        string="Program",
        ondelete="cascade"
    )

    is_global = fields.Boolean(
    string="Global Subject",
    default=False
    )

    category = fields.Selection(
        selection=[
            ('basic', 'Basic Mandatory'),
            ('extrinsic', 'Extrinsic Mandatory'),
            ('elective', 'Elective'),
        ],
        string="Category",
        required=True
    )

    semester = fields.Selection(
        [(str(i), str(i)) for i in range(1, 11)],
        string="Semester",
        required=True
    )

    number_credits = fields.Integer(
        string="Number of Credits",
        required=True
    )

    credit_value = fields.Float(
        string="Value per Credit",
        required=True
    )

    cost_subject = fields.Float(
        string="Total Cost",
        compute="_compute_cost_subject",
        store=True
    )

    max_enroll = fields.Integer(
        string="Maximum Students",
        default = 0
    )

    teacher_id = fields.Many2one(
        'res.users',
        string="Assigned Teacher",
        required=True
    )

    enrolment_ids = fields.One2many(
        'open.academy.enrolment',
        'subject_id',
        string="Enrollments"
    )

    student_count = fields.Integer(
        string="Enrolled Students",
        compute="_compute_student_count",
        store=True
    )
    
    active = fields.Boolean(
        string="Active",
        default=True
    )

    # Calcular costo automáticamente
    @api.depends('number_credits', 'credit_value')
    def _compute_cost_subject(self):
        for rec in self:
            rec.cost_subject = rec.number_credits * rec.credit_value

    # Contar estudiantes inscritos
    @api.depends('enrolment_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.enrolment_ids)

    # Validar cupo máximo
    # @api.constrains('max_enroll')
    # def _check_max_enroll(self):
    #     for rec in self:
    #         if rec.max_enroll <= 0:
    #             raise ValidationError(
    #                 "Maximum students must be greater than zero."
    #             )
    @api.constrains('subject_id')
    def _check_max_enroll(self):
        for rec in self:
            subject = rec.subject_id

            if not subject.is_global:
                if len(subject.enrolment_ids) > subject.max_enroll:
                    raise ValidationError(
                        "This subject has reached the maximum number of students."
    )
    # No permitir materias duplicadas en el mismo programa
    _unique_subject_per_program = models.Constraint(
        'UNIQUE(name, program_id)',
        'This subject already exists in this program.'
    )
