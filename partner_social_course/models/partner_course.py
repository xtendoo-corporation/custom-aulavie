from odoo import fields, models


class PartnerCourse(models.Model):
    _name = "partner.course"
    _description = "Curso de contacto"
    _order = "name"

    name = fields.Char(string="Curso", required=True)
    active = fields.Boolean(default=True)

