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

    @api.depends_context("uid")
    def _compute_aulavie_group_ids(self):
        Group = self.env["aulavie.groups"]
        for partner in self:
            partner.aulavie_group_ids = Group.search(
                [("contactos_ids", "in", partner.id)]
            )

    @api.depends("alumno_ids.user_ids")
    def _compute_alumno_user_ids(self):
        for partner in self:
            partner.alumno_user_ids = partner.alumno_ids.mapped("user_ids")
