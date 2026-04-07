import base64
import io
from datetime import datetime
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import openpyxl
except ImportError:
    openpyxl = None


class ImportAlumnosWizard(models.TransientModel):
    _name = "import.alumnos.wizard"
    _description = "Asistente para importar alumnos desde Excel"

    file = fields.Binary(string="Archivo Excel", required=True)
    filename = fields.Char(string="Nombre del archivo")

    def process_import(self):
        if not openpyxl:
            raise UserError(_("La librería openpyxl no está instalada en el servidor."))

        if not self.file:
            raise UserError(_("Por favor, suba un archivo Excel."))

        try:
            file_data = base64.b64decode(self.file)
            wb = openpyxl.load_workbook(filename=io.BytesIO(file_data), data_only=True)
            sheet = wb.active
        except Exception as e:
            raise UserError(_("No se pudo leer el archivo. Error: %s") % str(e))

        headers = [str(cell.value).strip().lower() if cell.value else "" for cell in sheet[1]]

        def get_col_idx(search_str):
            for i, h in enumerate(headers):
                if search_str in h:
                    return i
            return -1

        idx_nombre = get_col_idx("nombre y apellidos del alumno")
        if idx_nombre == -1:
            raise UserError(_("No se encontró la columna 'Nombre y apellidos del alumno/a'."))

        idx_direccion = get_col_idx("dirección del alumno")
        idx_fecha_nac = get_col_idx("fecha de nacimiento del alumno")
        idx_colegio = get_col_idx("colegio actual del alumno")
        idx_nivel = get_col_idx("nivel escolar")
        idx_alergias = get_col_idx("alergias o intolerancias del alumno")

        idx_tutor1_nombre = get_col_idx("nombre y apellido del tutor/a legal 1")
        idx_tutor1_dni = get_col_idx("dni/nif del tutor/a legal 1")
        idx_tutor1_tel = get_col_idx("teléfono móvil del tutor/a legal 1")
        idx_tutor1_email = get_col_idx("correo electrónico del tutor/a legal 1")

        idx_tutor2_nombre = get_col_idx("nombre y apellido del tutor/a legal 2")
        idx_tutor2_dni = get_col_idx("dni/nif del tutor/a legal 2")
        idx_tutor2_tel = get_col_idx("teléfono móvil del tutor/a legal 2")
        idx_tutor2_email = get_col_idx("correo electrónico del tutor/a legal 2")

        idx_autorizo = get_col_idx("autorizo al alumno")

        partner_obj = self.env['res.partner']
        alumnos_creados = 0

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            nombre = row[idx_nombre] if idx_nombre != -1 else None
            if not nombre:
                continue

            direccion = row[idx_direccion] if idx_direccion != -1 else False
            fecha_nac = row[idx_fecha_nac] if idx_fecha_nac != -1 else False
            colegio = row[idx_colegio] if idx_colegio != -1 else False
            nivel = row[idx_nivel] if idx_nivel != -1 else False
            alergias = row[idx_alergias] if idx_alergias != -1 else False

            t1_nom = row[idx_tutor1_nombre] if idx_tutor1_nombre != -1 else False
            t1_dni = row[idx_tutor1_dni] if idx_tutor1_dni != -1 else False
            t1_tel = row[idx_tutor1_tel] if idx_tutor1_tel != -1 else False
            t1_email = row[idx_tutor1_email] if idx_tutor1_email != -1 else False

            t2_nom = row[idx_tutor2_nombre] if idx_tutor2_nombre != -1 else False
            t2_dni = row[idx_tutor2_dni] if idx_tutor2_dni != -1 else False
            t2_tel = row[idx_tutor2_tel] if idx_tutor2_tel != -1 else False
            t2_email = row[idx_tutor2_email] if idx_tutor2_email != -1 else False

            autorizo_val = row[idx_autorizo] if idx_autorizo != -1 else ""
            autorizo_bool = False
            if autorizo_val:
                val_str = str(autorizo_val).lower().strip()
                if val_str in ["sí", "si", "x", "autorizo", "true", "1", "yes", "y", "autorizado", "todos", "algunos"]:
                    autorizo_bool = True

            # Parsear fecha de nacimiento
            fecha_nac_final = False
            if isinstance(fecha_nac, datetime):
                fecha_nac_final = fecha_nac.date()
            elif fecha_nac:
                fecha_nac_str = str(fecha_nac).split(' ')[0]
                try:
                    fecha_nac_final = datetime.strptime(fecha_nac_str, '%d/%m/%Y').date()
                except ValueError:
                    try:
                        fecha_nac_final = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
                    except ValueError:
                        pass

            # Preparar contactos hijos (Padre / Madre) usando campo nativo child_ids
            child_contacts = []

            if t1_nom:
                child_contacts.append((0, 0, {
                    'name': str(t1_nom),
                    'type': 'padre',
                    'vat': str(t1_dni) if t1_dni else False,
                    'phone': str(t1_tel) if t1_tel else False,
                    'email': str(t1_email) if t1_email else False,
                }))

            if t2_nom:
                child_contacts.append((0, 0, {
                    'name': str(t2_nom),
                    'type': 'madre',
                    'vat': str(t2_dni) if t2_dni else False,
                    'phone': str(t2_tel) if t2_tel else False,
                    'email': str(t2_email) if t2_email else False,
                }))

            # Buscar el ID del nivel escolar
            nivel_id = False
            if nivel:
                nivel_rec = self.env['nivel.escolar'].search([('name', '=ilike', str(nivel).strip())], limit=1)
                if nivel_rec:
                    nivel_id = nivel_rec.id

            vals = {
                'name': str(nombre),
                'rol_contacto': 'alumno',
                'is_company': False,
                'street': str(direccion) if direccion else False,
                'colegio_actual': str(colegio) if colegio else False,
                'nivel_escolar_id': nivel_id,
                'alergias_intolerancias': str(alergias) if alergias else False,
                'permitir_volver_solo_casa': autorizo_bool,
                'child_ids': child_contacts,
            }
            if fecha_nac_final:
                vals['fecha_nacimiento'] = fecha_nac_final

            partner_obj.create(vals)
            alumnos_creados += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Importación finalizada. Se han creado %s alumnos.') % alumnos_creados,
                'type': 'success',
                'sticky': False,
            }
        }
