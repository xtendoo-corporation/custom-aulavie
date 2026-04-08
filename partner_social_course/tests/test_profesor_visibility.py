# -*- coding: utf-8 -*-

from odoo.tests import common


class TestProfesorVisibility(common.TransactionCase):
    """Test de reglas de seguridad para profesores - solo ven sus grupos y alumnos"""

    def setUp(self):
        super(TestProfesorVisibility, self).setUp()

        # Crear usuarios y partners
        self.user_admin = self.env.ref('base.user_admin')

        # Profesor 1
        self.profesor1 = self.env['res.partner'].create({
            'name': 'Profesor Juan',
            'email': 'juan@profesor.com',
            'rol_contacto': 'profesor',
            'group_rfq': 'allowed',  # Campo requerido por módulo de compras
        })
        self.user_profesor1 = self.env['res.users'].create({
            'name': 'Juan Profesor',
            'login': 'profesor1',
            'email': 'juan@profesor.com',
            'partner_id': self.profesor1.id,
            'groups_id': [(4, self.env.ref('partner_social_course.group_profesor_aulavie').id)]
        })

        # Profesor 2 (otro profesor diferente)
        self.profesor2 = self.env['res.partner'].create({
            'name': 'Profesora María',
            'email': 'maria@profesor.com',
            'rol_contacto': 'profesor',
            'group_rfq': 'allowed',  # Campo requerido por módulo de compras
        })
        self.user_profesor2 = self.env['res.users'].create({
            'name': 'María Profesora',
            'login': 'profesor2',
            'email': 'maria@profesor.com',
            'partner_id': self.profesor2.id,
            'groups_id': [(4, self.env.ref('partner_social_course.group_profesor_aulavie').id)]
        })

        # Alumnos
        self.alumno1 = self.env['res.partner'].create({
            'name': 'Alumno Pedro',
            'email': 'pedro@alumno.com',
            'rol_contacto': 'alumno',
            'group_rfq': 'allowed',  # Campo requerido por módulo de compras
        })

        self.alumno2 = self.env['res.partner'].create({
            'name': 'Alumna Ana',
            'email': 'ana@alumno.com',
            'rol_contacto': 'alumno',
            'group_rfq': 'allowed',  # Campo requerido por módulo de compras
        })

        self.alumno3 = self.env['res.partner'].create({
            'name': 'Alumno Luis',
            'email': 'luis@alumno.com',
            'rol_contacto': 'alumno',
            'group_rfq': 'allowed',  # Campo requerido por módulo de compras
        })

        # Contacto sin relación (no debería verse)
        self.contacto_sin_relacion = self.env['res.partner'].create({
            'name': 'Cliente Externo',
            'email': 'cliente@externo.com',
            'group_rfq': 'allowed',  # Campo requerido por módulo de compras
        })

        # Crear días de la semana
        self.lunes = self.env['aulavie.days'].create({'nombre': 'Lunes'})
        self.miercoles = self.env['aulavie.days'].create({'nombre': 'Miércoles'})

        # Crear grupos
        self.grupo1_profesor1 = self.env['aulavie.groups'].create({
            'name': 'Matemáticas 1º ESO',
            'fecha_inicio': '2026-04-01',
            'hora_inicio': 9.0,
            'hora_fin': 10.0,
            'dias_ids': [(6, 0, [self.lunes.id])],
            'profesor_id': self.profesor1.id,
            'contactos_ids': [(6, 0, [self.alumno1.id, self.alumno2.id])],
        })

        self.grupo2_profesor1 = self.env['aulavie.groups'].create({
            'name': 'Matemáticas 2º ESO',
            'fecha_inicio': '2026-04-01',
            'hora_inicio': 11.0,
            'hora_fin': 12.0,
            'dias_ids': [(6, 0, [self.miercoles.id])],
            'profesor_id': self.profesor1.id,
            'contactos_ids': [(6, 0, [self.alumno3.id])],
        })

        self.grupo_profesor2 = self.env['aulavie.groups'].create({
            'name': 'Historia 1º ESO',
            'fecha_inicio': '2026-04-01',
            'hora_inicio': 9.0,
            'hora_fin': 10.0,
            'dias_ids': [(6, 0, [self.lunes.id])],
            'profesor_id': self.profesor2.id,
            'contactos_ids': [(6, 0, [self.alumno2.id, self.alumno3.id])],
        })

    def test_profesor_visible_ids_calculation(self):
        """Test que se calculan correctamente los profesor_visible_ids"""

        # Forzar recálculo
        all_partners = self.profesor1 | self.profesor2 | self.alumno1 | self.alumno2 | self.alumno3 | self.contacto_sin_relacion
        all_partners._compute_profesor_visible_ids()

        # Profesor 1 se ve a sí mismo
        self.assertIn(self.profesor1, self.profesor1.profesor_visible_ids)

        # Alumno 1 es visible para profesor 1 (está en grupo1_profesor1)
        self.assertIn(self.profesor1, self.alumno1.profesor_visible_ids)

        # Alumno 2 es visible para ambos profesores (está en ambos grupos)
        self.assertIn(self.profesor1, self.alumno2.profesor_visible_ids)
        self.assertIn(self.profesor2, self.alumno2.profesor_visible_ids)

        # Alumno 3 es visible para ambos profesores
        self.assertIn(self.profesor1, self.alumno3.profesor_visible_ids)
        self.assertIn(self.profesor2, self.alumno3.profesor_visible_ids)

        # Contacto sin relación no tiene profesores visibles
        self.assertEqual(len(self.contacto_sin_relacion.profesor_visible_ids), 0)

    def test_profesor1_ve_solo_sus_grupos(self):
        """Test que profesor1 solo ve sus grupos asignados"""

        # Cambiar a contexto de profesor1
        grupos_visibles = self.env['aulavie.groups'].sudo(self.user_profesor1).search([])

        # Profesor1 debe ver sus 2 grupos
        self.assertIn(self.grupo1_profesor1, grupos_visibles)
        self.assertIn(self.grupo2_profesor1, grupos_visibles)

        # Profesor1 NO debe ver el grupo de profesor2
        self.assertNotIn(self.grupo_profesor2, grupos_visibles)

        self.assertEqual(len(grupos_visibles), 2, "Profesor1 debe ver exactamente 2 grupos")

    def test_profesor2_ve_solo_sus_grupos(self):
        """Test que profesor2 solo ve su grupo asignado"""

        # Cambiar a contexto de profesor2
        grupos_visibles = self.env['aulavie.groups'].sudo(self.user_profesor2).search([])

        # Profesor2 debe ver solo su grupo
        self.assertIn(self.grupo_profesor2, grupos_visibles)

        # Profesor2 NO debe ver los grupos de profesor1
        self.assertNotIn(self.grupo1_profesor1, grupos_visibles)
        self.assertNotIn(self.grupo2_profesor1, grupos_visibles)

        self.assertEqual(len(grupos_visibles), 1, "Profesor2 debe ver exactamente 1 grupo")

    def test_profesor1_ve_solo_sus_contactos(self):
        """Test que profesor1 solo ve sus alumnos y a sí mismo"""

        # Forzar recálculo de visibilidad
        all_partners = self.profesor1 | self.profesor2 | self.alumno1 | self.alumno2 | self.alumno3 | self.contacto_sin_relacion
        all_partners._compute_profesor_visible_ids()

        # Cambiar a contexto de profesor1
        contactos_visibles = self.env['res.partner'].sudo(self.user_profesor1).search([])

        # Profesor1 debe verse a sí mismo
        self.assertIn(self.profesor1, contactos_visibles)

        # Profesor1 debe ver a sus alumnos (alumno1, alumno2, alumno3)
        self.assertIn(self.alumno1, contactos_visibles, "Profesor1 debe ver alumno1 (en su grupo)")
        self.assertIn(self.alumno2, contactos_visibles, "Profesor1 debe ver alumno2 (en su grupo)")
        self.assertIn(self.alumno3, contactos_visibles, "Profesor1 debe ver alumno3 (en su grupo)")

        # Profesor1 NO debe ver al profesor2
        self.assertNotIn(self.profesor2, contactos_visibles, "Profesor1 NO debe ver a profesor2")

        # Profesor1 NO debe ver contactos sin relación
        self.assertNotIn(self.contacto_sin_relacion, contactos_visibles, "Profesor1 NO debe ver contactos externos")

    def test_profesor2_ve_solo_sus_contactos(self):
        """Test que profesor2 solo ve sus alumnos y a sí mismo"""

        # Forzar recálculo de visibilidad
        all_partners = self.profesor1 | self.profesor2 | self.alumno1 | self.alumno2 | self.alumno3 | self.contacto_sin_relacion
        all_partners._compute_profesor_visible_ids()

        # Cambiar a contexto de profesor2
        contactos_visibles = self.env['res.partner'].sudo(self.user_profesor2).search([])

        # Profesor2 debe verse a sí mismo
        self.assertIn(self.profesor2, contactos_visibles)

        # Profesor2 debe ver a sus alumnos (alumno2 y alumno3, que están en su grupo)
        self.assertIn(self.alumno2, contactos_visibles, "Profesor2 debe ver alumno2 (en su grupo)")
        self.assertIn(self.alumno3, contactos_visibles, "Profesor2 debe ver alumno3 (en su grupo)")

        # Profesor2 NO debe ver al alumno1 (solo está en grupos de profesor1)
        self.assertNotIn(self.alumno1, contactos_visibles, "Profesor2 NO debe ver alumno1 (no en sus grupos)")

        # Profesor2 NO debe ver al profesor1
        self.assertNotIn(self.profesor1, contactos_visibles, "Profesor2 NO debe ver a profesor1")

        # Profesor2 NO debe ver contactos sin relación
        self.assertNotIn(self.contacto_sin_relacion, contactos_visibles, "Profesor2 NO debe ver contactos externos")

    def test_profesor_ve_sesiones_solo_de_sus_grupos(self):
        """Test que cada profesor solo ve sesiones de sus grupos"""

        # Las sesiones se crean automáticamente al crear los grupos
        # Cambiar a contexto de profesor1
        sesiones_profesor1 = self.env['aulavie.sesiones'].sudo(self.user_profesor1).search([])

        # Todas las sesiones visibles deben ser de grupos del profesor1
        for sesion in sesiones_profesor1:
            self.assertIn(sesion.grupo_id, [self.grupo1_profesor1, self.grupo2_profesor1],
                         "Profesor1 solo debe ver sesiones de sus grupos")

        # Cambiar a contexto de profesor2
        sesiones_profesor2 = self.env['aulavie.sesiones'].sudo(self.user_profesor2).search([])

        # Todas las sesiones visibles deben ser del grupo del profesor2
        for sesion in sesiones_profesor2:
            self.assertEqual(sesion.grupo_id, self.grupo_profesor2,
                           "Profesor2 solo debe ver sesiones de su grupo")

    def test_admin_ve_todo(self):
        """Test que el admin sigue viendo todos los registros (no afectado por las reglas)"""

        # Admin debe ver todos los grupos
        todos_grupos = self.env['aulavie.groups'].sudo(self.user_admin).search([])
        self.assertIn(self.grupo1_profesor1, todos_grupos)
        self.assertIn(self.grupo2_profesor1, todos_grupos)
        self.assertIn(self.grupo_profesor2, todos_grupos)

        # Admin debe ver todos los contactos
        todos_contactos = self.env['res.partner'].sudo(self.user_admin).search([])
        self.assertIn(self.profesor1, todos_contactos)
        self.assertIn(self.profesor2, todos_contactos)
        self.assertIn(self.alumno1, todos_contactos)
        self.assertIn(self.alumno2, todos_contactos)
        self.assertIn(self.alumno3, todos_contactos)
        self.assertIn(self.contacto_sin_relacion, todos_contactos)

    def test_cambio_contactos_actualiza_visibilidad(self):
        """Test que al cambiar contactos de un grupo se actualiza profesor_visible_ids"""

        # Estado inicial: alumno1 solo visible para profesor1
        all_partners = self.profesor1 | self.profesor2 | self.alumno1 | self.alumno2 | self.alumno3 | self.contacto_sin_relacion
        all_partners._compute_profesor_visible_ids()

        self.assertIn(self.profesor1, self.alumno1.profesor_visible_ids)
        self.assertNotIn(self.profesor2, self.alumno1.profesor_visible_ids)

        # Añadir alumno1 al grupo del profesor2
        self.grupo_profesor2.write({
            'contactos_ids': [(4, self.alumno1.id)]
        })

        # Ahora alumno1 debe ser visible para ambos profesores
        self.assertIn(self.profesor1, self.alumno1.profesor_visible_ids)
        self.assertIn(self.profesor2, self.alumno1.profesor_visible_ids)

        # Quitar alumno1 del grupo del profesor1
        self.grupo1_profesor1.write({
            'contactos_ids': [(3, self.alumno1.id)]
        })

        # Ahora alumno1 solo debe ser visible para profesor2
        self.assertNotIn(self.profesor1, self.alumno1.profesor_visible_ids)
        self.assertIn(self.profesor2, self.alumno1.profesor_visible_ids)

    def test_cambio_profesor_actualiza_visibilidad(self):
        """Test que al cambiar el profesor de un grupo se actualiza profesor_visible_ids"""

        # Estado inicial
        all_partners = self.profesor1 | self.profesor2 | self.alumno1 | self.alumno2 | self.alumno3
        all_partners._compute_profesor_visible_ids()

        # alumno1 visible solo para profesor1
        self.assertIn(self.profesor1, self.alumno1.profesor_visible_ids)
        self.assertNotIn(self.profesor2, self.alumno1.profesor_visible_ids)

        # Cambiar profesor del grupo1 a profesor2
        self.grupo1_profesor1.write({
            'profesor_id': self.profesor2.id
        })

        # Ahora alumno1 debe ser visible para profesor2 (y posiblemente ya no para profesor1)
        self.assertIn(self.profesor2, self.alumno1.profesor_visible_ids)
