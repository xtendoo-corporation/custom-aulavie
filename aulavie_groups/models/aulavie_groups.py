# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class AulavieGroups(models.Model):
    _name = "aulavie.groups"
    _description = "Grupos de Aulavie"
    _order = "name"

    name = fields.Char(
        string="Nombre del Grupo",
        required=True,
    )

    fecha_inicio = fields.Date(
        string="Fecha de Inicio",
        required=True,
        default=fields.Date.today,
        help="Fecha desde la cual se generarán las sesiones",
    )

    dias_ids = fields.Many2many(
        "aulavie.days",
        string="Días de la Semana",
        required=True,
    )

    hora_inicio = fields.Float(
        string="Hora Inicio",
        required=True,
    )

    hora_fin = fields.Float(
        string="Hora Fin",
        required=True,
    )

    contactos_ids = fields.Many2many(
        "res.partner",
        string="Contactos",
    )

    sesion_ids = fields.One2many(
        "aulavie.sesiones",
        "grupo_id",
        string="Sesiones",
    )

    def write(self, vals):
        result = super(AulavieGroups, self).write(vals)
        self._generar_sesiones()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AulavieGroups, self).create(vals_list)
        records._generar_sesiones()
        return records

    def _generar_sesiones(self):
        """Genera sesiones para las próximas 4 semanas"""
        Sesion = self.env["aulavie.sesiones"]

        # Mapeo de días
        mapa_dias = {
            "Lunes": 0,
            "Martes": 1,
            "Miércoles": 2,
            "Jueves": 3,
            "Viernes": 4,
            "Sábado": 5,
            "Domingo": 6,
        }

        for grupo in self:
            # Eliminar sesiones antiguas
            grupo.sesion_ids.unlink()

            # Crear nuevas sesiones para las próximas 4 semanas
            for dia in grupo.dias_ids:
                dia_semana = mapa_dias.get(dia.nombre)
                if dia_semana is None:
                    continue

                # Generar 4 sesiones (una por semana)
                for semana in range(4):
                    # Calcular la fecha
                    dias_adelante = dia_semana - grupo.fecha_inicio.weekday()
                    if dias_adelante < 0:
                        dias_adelante += 7
                    fecha_sesion = grupo.fecha_inicio + timedelta(
                        days=dias_adelante + (semana * 7)
                    )

                    # Convertir horas
                    hora_inicio = int(grupo.hora_inicio)
                    minuto_inicio = int((grupo.hora_inicio - hora_inicio) * 60)
                    hora_fin = int(grupo.hora_fin)
                    minuto_fin = int((grupo.hora_fin - hora_fin) * 60)

                    # Crear datetime
                    fecha_hora_inicio = datetime.combine(
                        fecha_sesion, datetime.min.time()
                    ).replace(hour=hora_inicio, minute=minuto_inicio)
                    fecha_hora_fin = datetime.combine(
                        fecha_sesion, datetime.min.time()
                    ).replace(hour=hora_fin, minute=minuto_fin)

                    # Crear sesión
                    Sesion.create(
                        {
                            "grupo_id": grupo.id,
                            "dia_id": dia.id,
                            "fecha_hora_inicio": fecha_hora_inicio,
                            "fecha_hora_fin": fecha_hora_fin,
                        }
                    )
