# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class AulavieSesiones(models.Model):
    _name = 'aulavie.sesiones'
    _description = 'Sesiones de Grupo'
    _order = 'fecha_hora_inicio'

    nombre = fields.Char(
        string='Nombre',
        compute='_compute_nombre',
        store=True,
    )

    grupo_id = fields.Many2one(
        'aulavie.groups',
        string='Grupo',
        required=True,
        ondelete='cascade',
    )

    dia_id = fields.Many2one(
        'aulavie.days',
        string='Día',
        required=True,
    )

    fecha_hora_inicio = fields.Datetime(
        string='Inicio',
        required=True,
    )

    fecha_hora_fin = fields.Datetime(
        string='Fin',
        required=True,
    )

    contactos_ids = fields.Many2many(
        related='grupo_id.contactos_ids',
        string='Contactos',
    )

    @api.depends('grupo_id.name', 'dia_id.nombre')
    def _compute_nombre(self):
        for sesion in self:
            if sesion.grupo_id and sesion.dia_id:
                sesion.nombre = f"{sesion.grupo_id.name} - {sesion.dia_id.nombre}"
            else:
                sesion.nombre = "Sesión"
