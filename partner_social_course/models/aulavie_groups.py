from odoo import api, fields, models


class AulavieGroups(models.Model):
    _inherit = "aulavie.groups"

    profesor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Profesor",
        domain=[("rol_contacto", "=", "profesor")],
        help="Profesor asignado a este grupo",
    )

    def _recompute_profesor_visible(self, extra_partners=None):
        """Recalcula profesor_visible_ids en los contactos de estos grupos."""
        partners = self.mapped("contactos_ids") | self.mapped("profesor_id")
        if extra_partners:
            partners |= extra_partners
        if partners:
            partners._compute_profesor_visible_ids()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._recompute_profesor_visible()
        return records

    def write(self, vals):
        # Guardar contactos anteriores para recalcular también los eliminados
        old_partners = self.mapped("contactos_ids") | self.mapped("profesor_id")
        result = super().write(vals)
        self._recompute_profesor_visible(extra_partners=old_partners)
        return result

