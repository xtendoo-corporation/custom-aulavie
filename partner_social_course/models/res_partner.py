from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    permitir_salir_redes_sociales = fields.Boolean(
        string="Permitir salir en redes sociales",
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
        compute="_compute_rol_contacto",
        store=True,
        default="alumno",
        tracking=True,
    )

    @api.depends("user_ids", "user_ids.share")
    def _compute_rol_contacto(self):
        """Un partner con un usuario interno (share=False) es 'profesor',
        el resto es 'alumno'."""
        for partner in self:
            if partner.user_ids.filtered(lambda u: not u.share):
                partner.rol_contacto = "profesor"
            else:
                partner.rol_contacto = "alumno"

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

    # Profesores que pueden ver este contacto (stored para ir.rule)
    profesor_visible_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="partner_profesor_visible_rel",
        column1="partner_id",
        column2="profesor_id",
        string="Profesores que ven este contacto",
        compute="_compute_profesor_visible_ids",
        store=True,
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

    # Añadir tipos Padre, Madre y tutor legal al campo nativo de Odoo
    type = fields.Selection(
        selection_add=[
            ("padre", "Padre"),
            ("madre", "Madre"),
            ("tutor legal", "Tutor legal"),
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

    @api.depends("user_ids", "aulavie_group_ids")
    def _compute_profesor_visible_ids(self):
        """Calcula qué profesores pueden ver cada contacto.
        Un profesor ve un contacto si este aparece en contactos_ids
        de algún grupo donde ese profesor es profesor_id.
        También el propio profesor se ve a sí mismo.
        NOTA: se recalcula también desde aulavie.groups.write/create."""
        Group = self.env["aulavie.groups"].sudo()
        for partner in self:
            groups = Group.search([("contactos_ids", "in", partner.id)])
            profesores = groups.mapped("profesor_id")
            if partner.rol_contacto == "profesor":
                profesores |= partner
            partner.profesor_visible_ids = profesores

