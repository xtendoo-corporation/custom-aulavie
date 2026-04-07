from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    permitir_salir_redes_sociales = fields.Boolean(
        string="Permitir salir en redes sociales",
    )
    curso_ids = fields.Many2many(
        comodel_name="partner.course",
        relation="res_partner_partner_course_rel",
        column1="partner_id",
        column2="course_id",
        string="Cursos",
    )
    aulavie_group_ids = fields.Many2many(
        comodel_name="aulavie.groups",
        string="Grupos Aulavie",
        compute="_compute_aulavie_group_ids",
    )
    rol_contacto = fields.Selection(
        selection=[
            ("alumno", "Alumno"),
            ("profesor", "Profesor"),
        ],
        string="Rol",
        default="alumno",
        tracking=True,
    )
    profesor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Profesor",
        domain=[("rol_contacto", "=", "profesor")],
    )
    alumno_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="profesor_id",
        string="Alumnos",
    )
    alumno_user_ids = fields.Many2many(
        comodel_name="res.users",
        compute="_compute_alumno_user_ids",
        string="Usuarios alumnos",
    )
    profesor_grupo_ids = fields.One2many(
        comodel_name="aulavie.groups",
        inverse_name="profesor_id",
        string="Grupos como Profesor",
    )

    fecha_nacimiento = fields.Date(
        string="Fecha de nacimiento",
    )
    colegio_actual = fields.Char(
        string="Colegio actual",
    )
    nivel_escolar_id = fields.Many2one(
        'nivel.escolar', string='Nivel escolar', ondelete='set null'
    )
    alergias_intolerancias = fields.Text(
        string="Alergias o intolerancias",
    )
    tiene_necesidades_especiales = fields.Boolean(
        string="¿Tiene necesidades especiales?",
    )
    necesidades_especiales_detalle = fields.Text(
        string="Detalle de necesidades especiales",
    )
    permitir_volver_solo_casa = fields.Boolean(
        string="¿Permites al alumno menor volver solo a casa?",
    )

    # Añadir tipos Padre y Madre al campo nativo de Odoo
    type = fields.Selection(
        selection_add=[
            ("padre", "Padre / Tutor legal 1"),
            ("madre", "Madre / Tutor legal 2"),
        ],
        ondelete={"padre": "set default", "madre": "set default"},
    )

    @api.depends("profesor_grupo_ids")
    @api.depends_context("uid")
    def _compute_aulavie_group_ids(self):
        Group = self.env["aulavie.groups"]
        for partner in self:
            as_contact = Group.search(
                [("contactos_ids", "in", partner.id)]
            )
            as_profesor = partner.profesor_grupo_ids
            partner.aulavie_group_ids = as_contact | as_profesor

    @api.depends("alumno_ids.user_ids")
    def _compute_alumno_user_ids(self):
        for partner in self:
            partner.alumno_user_ids = partner.alumno_ids.mapped("user_ids")
