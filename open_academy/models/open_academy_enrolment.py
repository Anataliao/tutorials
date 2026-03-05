from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpenAcademyEnrolment(models.Model):
    _name = 'open.academy.enrolment'
    _description = 'Subject Enrolment'
    _order = 'subject_id'

    registration_id = fields.Many2one(
        'open.academy.registration',
        string="Registration",
        required=True,
        ondelete="cascade",
        domain=lambda self: [
            ('student_id.user_id', '=', self.env.uid)
        ],
        default=lambda self: self._get_default_registration()
    )
    
    user_id = fields.Many2one(
        related='registration_id.student_id.user_id',
        string="Assigned Student",
        store=True,
        readonly=True
    )
    
    student_id = fields.Many2one(
        related='registration_id.student_id.user_id',
        store=True,
        string="Student"
    )

    program_id = fields.Many2one(
        related='registration_id.program_id',
        store=True,
        string="Program"
    )

    current_semester = fields.Selection(
        related='registration_id.current_semester',
        store=True,
        string="Current Semester"
    )
    
    subject_id = fields.Many2one(
        'open.academy.subject',
        string="Subject",
        required=True
    )

    credits = fields.Integer(
        related='subject_id.number_credits',
        store=True,
        string="Credits"
    )

    grade_id = fields.One2many(
        'open.academy.grade',
        'enrolment_id',
        string="Grade"
    )
    @api.constrains('subject_id')
    def _check_prerequisite(self):
        for rec in self:
            prereq = rec.subject_id.prerequisite_id
            if prereq:
                # Buscar si el estudiante tiene una nota aprobada en esa materia
                # 3.0 es la nota mínima para pasar
                passed = self.env['open.academy.grade'].search([
                    ('student_id', '=', rec.student_id.id),
                    ('subject_id', '=', prereq.id),
                    ('final_grade', '>', 3.0)
                ], limit=1)

                if not passed:
                    raise ValidationError(
                        f"Registration Blocked! You cannot register'{rec.subject_id.name}' "
                        f"because you have not passed the prerequisite:'{prereq.name}'."
                    )
    def _get_default_registration(self):
        registrations = self.env['open.academy.registration'].search(
            [('student_id.user_id', '=', self.env.uid)]
        )
        # Si solo tiene una carrera la pone automática
        if len(registrations) == 1:
            return registrations.id
        # Si tiene varias → que elija
        return False

    # CREAR AUTOMÁTICAMENTE REGISTRO DE NOTA 
    @api.model_create_multi
    def create(self, vals_list):
        enrolments = super().create(vals_list)

        grade_vals = []
        for enrolment in enrolments:
            grade_vals.append({
                'enrolment_id': enrolment.id
            })
        # Crear las notas
        if grade_vals:
            self.env['open.academy.grade'].sudo().create(grade_vals)

        return enrolments

    # VALIDAR QUE LA MATERIA SEA DEL PROGRAMA
    @api.constrains('subject_id', 'program_id')
    def _check_subject_program(self):
        for rec in self:
            if  (not rec.subject_id.is_global and 
                    rec.subject_id.program_id != rec.program_id):
                raise ValidationError(
                    "You cannot enroll in a subject from another program."
                )

    # VALIDAR SEMESTRE CORRECTO
    @api.constrains('subject_id', 'registration_id')
    def _check_semester(self):
        for rec in self:
            if (not rec.subject_id.is_global and
                    rec.subject_id.program_id != rec.program_id):
                raise ValidationError(
                    "You cannot enroll in a subject from another program."
                )

    # VALIDAR QUE NO LA HAYA APROBADO ANTES
    @api.constrains('subject_id', 'student_id')
    def _check_already_passed(self):
        for rec in self:
            previous = self.search([
                ('student_id', '=', rec.student_id.id),
                ('subject_id', '=', rec.subject_id.id),
                ('grade_id.final_grade', '>=', 3.1),
                ('id', '!=', rec.id)
            ])

            if previous:
                raise ValidationError(
                    "You already passed this subject."
                )

    # NO DUPLICAR MATERIA EN MISMA MATRÍCULA
    _unique_subject_registration = models.Constraint(
        'UNIQUE(registration_id, subject_id)',
        'You are already enrolled in this subject.'
    )
