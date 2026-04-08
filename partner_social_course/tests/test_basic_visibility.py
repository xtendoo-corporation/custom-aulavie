# -*- coding: utf-8 -*-

from odoo.tests import common


class TestBasicProfesorVisibility(common.TransactionCase):
    """Test básico para verificar las reglas de visibilidad del profesor"""

    def test_01_basic_setup(self):
        """Test básico: crear registros y verificar que no falla"""

        # Crear profesor con campos mínimos
        profesor = self.env['res.partner'].create({
            'name': 'Prof Test',
            'rol_contacto': 'profesor',
            'is_company': False,
        })

        # Crear usuario profesor
        user_profesor = self.env['res.users'].create({
            'name': 'Prof User',
            'login': 'proftest',
            'partner_id': profesor.id,
            'groups_id': [(4, self.env.ref('partner_social_course.group_profesor_aulavie').id)]
        })

        # Crear alumno
        alumno = self.env['res.partner'].create({
            'name': 'Alumno Test',
            'rol_contacto': 'alumno',
            'is_company': False,
        })

        # Crear días y grupo
        lunes = self.env['aulavie.days'].create({'nombre': 'Lunes'})

        grupo = self.env['aulavie.groups'].create({
            'name': 'Matemáticas Test',
            'fecha_inicio': '2026-04-01',
            'hora_inicio': 9.0,
            'hora_fin': 10.0,
            'dias_ids': [(6, 0, [lunes.id])],
            'profesor_id': profesor.id,
            'contactos_ids': [(6, 0, [alumno.id])],
        })

        # Verificaciones básicas
        self.assertEqual(profesor.rol_contacto, 'profesor')
        self.assertEqual(alumno.rol_contacto, 'alumno')
        self.assertEqual(grupo.profesor_id, profesor)
        self.assertIn(alumno, grupo.contactos_ids)

        # Test de campo computed profesor_visible_ids
        alumno._compute_profesor_visible_ids()
        self.assertIn(profesor, alumno.profesor_visible_ids,
                     "El alumno debe ser visible para su profesor")

        # Test de ir.rule básica - profesor ve su grupo
        grupos_visibles = self.env['aulavie.groups'].sudo(user_profesor).search([])
        self.assertIn(grupo, grupos_visibles, "Profesor debe ver su grupo")

        print("✅ Test básico completado correctamente")

    def test_02_profesor_isolation(self):
        """Test que un profesor no ve grupos de otros profesores"""

        # Crear dos profesores
        profesor1 = self.env['res.partner'].create({
            'name': 'Prof 1',
            'rol_contacto': 'profesor',
            'is_company': False,
        })

        profesor2 = self.env['res.partner'].create({
            'name': 'Prof 2',
            'rol_contacto': 'profesor',
            'is_company': False,
        })

        # Usuarios
        user_prof1 = self.env['res.users'].create({
            'name': 'User Prof 1',
            'login': 'prof1',
            'partner_id': profesor1.id,
            'groups_id': [(4, self.env.ref('partner_social_course.group_profesor_aulavie').id)]
        })

        user_prof2 = self.env['res.users'].create({
            'name': 'User Prof 2',
            'login': 'prof2',
            'partner_id': profesor2.id,
            'groups_id': [(4, self.env.ref('partner_social_course.group_profesor_aulavie').id)]
        })

        # Días
        lunes = self.env['aulavie.days'].create({'nombre': 'Lunes'})

        # Grupos separados
        grupo1 = self.env['aulavie.groups'].create({
            'name': 'Grupo Prof 1',
            'fecha_inicio': '2026-04-01',
            'hora_inicio': 9.0,
            'hora_fin': 10.0,
            'dias_ids': [(6, 0, [lunes.id])],
            'profesor_id': profesor1.id,
        })

        grupo2 = self.env['aulavie.groups'].create({
            'name': 'Grupo Prof 2',
            'fecha_inicio': '2026-04-01',
            'hora_inicio': 11.0,
            'hora_fin': 12.0,
            'dias_ids': [(6, 0, [lunes.id])],
            'profesor_id': profesor2.id,
        })

        # Test aislamiento
        grupos_prof1 = self.env['aulavie.groups'].sudo(user_prof1).search([])
        grupos_prof2 = self.env['aulavie.groups'].sudo(user_prof2).search([])

        self.assertIn(grupo1, grupos_prof1, "Prof1 debe ver su grupo")
        self.assertNotIn(grupo2, grupos_prof1, "Prof1 NO debe ver grupo de Prof2")

        self.assertIn(grupo2, grupos_prof2, "Prof2 debe ver su grupo")
        self.assertNotIn(grupo1, grupos_prof2, "Prof2 NO debe ver grupo de Prof1")

        print("✅ Test aislamiento profesores completado correctamente")
