# -*- coding: utf-8 -*-

from odoo import models, fields


class AulavieDays(models.Model):
    _name = 'aulavie.days'
    _description = 'Días de la Semana'
    _order = 'secuencia'
    _rec_name = 'nombre'

    nombre = fields.Char(
        string='Nombre del Día',
        required=True,
    )

    secuencia = fields.Integer(
        string='Secuencia',
        default=10,
    )
