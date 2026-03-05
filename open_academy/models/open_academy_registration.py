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

    sequence = fields.Integer()

    student_id = fields.Many2one(
        'open.academy.student',
        string="Student",
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

    @api.model_create_multi
    def create(self, vals_list):
        # crear ergistro 
        registrations = super(OpenAcademyRegistration, self).create(vals_list)
        for reg in registrations:
            #1 semestre incribe las materias 
            if reg.current_semester == '1':
                reg._auto_enroll_first_semester()
        return registrations

    def write(self, vals):
        # Guardar semestres actuales
        old_semesters = {reg.id: int(reg.current_semester) for reg in self}
        
        res = super(OpenAcademyRegistration, self).write(vals)
        
        if 'current_semester' in vals:
            new_sem_int = int(vals.get('current_semester'))
            for reg in self:
                # Si el estudiante subió de semestre
                if new_sem_int > old_semesters.get(reg.id, 0):
                    # se inscr9ibe automáticamente las que perdió en semestres pasados
                    reg._enroll_failed_subjects()
                
                # Si lo bajaron a semestre 1 manualmente, inscribe materias de 1ero
                if vals.get('current_semester') == '1':
                    reg._auto_enroll_first_semester()
        return res

    def _enroll_failed_subjects(self):
        #Busca materias reprobadas y las inscribe en la matrícula actual
        for reg in self:

            failed_enrolments = self.env['open.academy.enrolment'].search([
                ('student_id', '=', reg.student_id.user_id.id),
                ('grade_id.final_grade', '<', 3.0),
                ('grade_id.final_grade', '>', 0) # Solo las que ya tienen nota cargada
            ])
            
            subjects_to_retry = failed_enrolments.mapped('subject_id')
            enrolment_vals = []
            
            for subject in subjects_to_retry:
                # evita duplicar materias 
                exists = self.env['open.academy.enrolment'].search_count([
                    ('registration_id', '=', reg.id),
                    ('subject_id', '=', subject.id)
                ])
                if not exists:
                    enrolment_vals.append({
                        'registration_id': reg.id,
                        'subject_id': subject.id,
                    })
            # crear incripciones de las perdidas
            if enrolment_vals:
                self.env['open.academy.enrolment'].create(enrolment_vals)

    def _check_and_promote_student(self):
        #mirar si tiene todas las notas y decide si pasa de semestre 
        for reg in self.sudo():
            if not reg.enrolment_ids:
                continue
                
            # mira si tiene todas las materias nota final
            all_graded = all(enro.grade_id.final_grade > 0 for enro in reg.enrolment_ids)
            
            if all_graded:
                # Identificar aprobadas y reprobadad
                passed_enrolments = reg.enrolment_ids.filtered(lambda e: e.grade_id.final_grade >= 3.0)
                failed_enrolments = reg.enrolment_ids.filtered(lambda e: e.grade_id.final_grade < 3.0)

                # Borramor las aprobadas de la vista actual 
                if passed_enrolments:
                    passed_enrolments.unlink()

                # cambia de semestre 
                current_sem = int(reg.current_semester)
                if current_sem < 10:
                    reg.write({'current_semester': str(current_sem + 1)})
                
    def _auto_enroll_first_semester(self):
        for reg in self:
            #busacar materias de 1 semestre 
            subjects = self.env['open.academy.subject'].search([
                ('program_id', '=', reg.program_id.id),
                ('semester', '=', '1'),
                ('active', '=', True)
            ])
            enrolment_vals = []
            for subject in subjects:
                #evitar duplicados
                existing = self.env['open.academy.enrolment'].search_count([
                    ('registration_id', '=', reg.id),
                    ('subject_id', '=', subject.id)
                ])
                if not existing:
                    enrolment_vals.append({'registration_id': reg.id, 'subject_id': subject.id})
            if enrolment_vals:
                self.env['open.academy.enrolment'].create(enrolment_vals)
    
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

    @api.constrains('student_id', 'active')
    def _check_max_active_registrations(self):
        for rec in self:
            if rec.active:
                # Contamos cuántas matrículas activas tiene el estudiante en TOTAL
                active_count = self.search_count([
                    ('student_id', '=', rec.student_id.id),
                    ('active', '=', True)
                ])
                
                # Si el conteo es mayor a 2 error
                if active_count > 2:
                    raise ValidationError(
                        f"Limit reached! The student {rec.student_id.name} "
                        "You cannot have more than 2 active careers simultaneously."
                    )
    @api.constrains('student_id', 'program_id')
    def _check_already_registered(self):
        for rec in self:
            # Buscamos si ya existe un registro para este alumno y este programa
            domain = [
                ('student_id', '=', rec.student_id.id),
                ('program_id', '=', rec.program_id.id),
                ('id', '!=', rec.id), # Evitamos que se encuentre a sí mismo
            ]

# No permitir 2 matrículas activas del mismo programa
    _unique_active_program = models.Constraint(
        'UNIQUE(student_id, program_id, active)',
        'The student already has an active registration for this program.'
    )
