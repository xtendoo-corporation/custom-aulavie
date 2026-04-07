from odoo import models, fields


class NivelEscolar(models.Model):
    _name = 'nivel.escolar'
    _description = 'Niveles escolares en España'
    _order = 'orden, name'

    name = fields.Char(string='Nivel Escolar', required=True)


    orden = fields.Integer(string='Orden',
                           help='Orden del nivel dentro de la estructura educativa.'
                           )

    estudiante_ids = fields.One2many(
        'res.partner',
        'nivel_escolar_id',
        string='Estudiantes'
    )

    _sql_constraints = [
        ('nivel_escolar_name_uniq', 'unique(name)', 'El nivel escolar ya existe.'),
    ]
