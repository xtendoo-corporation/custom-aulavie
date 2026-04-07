from odoo import fields, models


class AulavieGroups(models.Model):
    _inherit = "aulavie.groups"

    profesor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Profesor",
        domain=[("rol_contacto", "=", "profesor")],
        help="Profesor asignado a este grupo",
    )

