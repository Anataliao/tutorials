from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpenAcademyGrade(models.Model):
    _name = 'open.academy.grade'
    _description = 'Subject Grade'
    _order = 'subject_id'

    enrolment_id = fields.Many2one(
        'open.academy.enrolment',
        string="Enrolment",
        required=True,
        ondelete="cascade"
    )

    subject_id = fields.Many2one(
        related='enrolment_id.subject_id',
        store=True,
        string="Subject"
    )

    teacher_id = fields.Many2one(
        related='subject_id.teacher_id',
        store=True,
        string="Teacher"
    )

    student_id = fields.Many2one(
        related='enrolment_id.student_id',
        store=True,
        string="Student"
    )

    cut1 = fields.Float(string="Cut 1 (30%)")
    cut2 = fields.Float(string="Cut 2 (30%)")
    cut3 = fields.Float(string="Cut 3 (40%)")

    final_grade = fields.Float(
        string="Final Grade",
        compute="_compute_final_grade",
        store=True
    )

    approved = fields.Boolean(
        string="Approved",
        compute="_compute_approved",
        store=True
    )

    # SUMATORIA Y APROBACION DE MATERIAS 
    @api.depends('cut1', 'cut2', 'cut3')
    def _compute_final_grade(self):
        for rec in self:
            rec.final_grade = (
                (rec.cut1 * 0.3) +
                (rec.cut2 * 0.3) +
                (rec.cut3 * 0.4)
            )
            rec.approved = rec.final_grade > 3.0

    def write(self, vals):
        # Guardar cambios de la nota
        res = super(OpenAcademyGrade, self).write(vals)
        
        # mirar si cambiaron (notas)
        if any(field in vals for field in ['cut1', 'cut2', 'cut3']):
            for grade in self:
                # Buscar la matrícula de esta nota
                registration = grade.enrolment_id.registration_id.sudo()
                if registration:
                    # mirar se pasa semestre
                    registration._check_and_promote_student()
        return res

    # VALIDAR RANGO DE NOTAS (0 - 5)
    @api.constrains('cut1', 'cut2', 'cut3')
    def _check_grade_range(self):
        for rec in self:
            for grade in [rec.cut1, rec.cut2, rec.cut3]:
                if grade < 0 or grade > 5:
                    raise ValidationError(
                        "Grades must be between 0 and 5."
                    )

    # SOLO UNA NOTA POR INSCRIPCIÓN
    _unique_enrolment_grade = models.Constraint(
        'UNIQUE(enrolment_id)',
        'A grade already exists for this subject.'
    )
