from odoo.tests.common import TransactionCase


class TestPartnerRol(TransactionCase):

    def setUp(self):
        super().setUp()

        # Crear partner profesor
        self.profesor = self.env["res.partner"].create({
            "name": "Profesor Test",
            "email": "profesor@test.com",
            "rol_contacto": "profesor",
        })

        # Crear partner alumno 1
        self.alumno1 = self.env["res.partner"].create({
            "name": "Alumno Test 1",
            "email": "alumno1@test.com",
            "rol_contacto": "alumno",
            "profesor_id": self.profesor.id,
        })

        # Crear partner alumno 2
        self.alumno2 = self.env["res.partner"].create({
            "name": "Alumno Test 2",
            "email": "alumno2@test.com",
            "rol_contacto": "alumno",
            "profesor_id": self.profesor.id,
        })

        # Grupos de seguridad
        self.group_alumno = self.env.ref(
            "partner_social_course.group_aulavie_alumno"
        )
        self.group_profesor = self.env.ref(
            "partner_social_course.group_aulavie_profesor"
        )

    # ---------------------------------------------------------
    # TEST 1: Verificar que el rol se guarda correctamente
    # ---------------------------------------------------------
    def test_01_rol_contacto_profesor(self):
        """El partner profesor debe tener rol_contacto = 'profesor'"""
        self.assertEqual(
            self.profesor.rol_contacto,
            "profesor",
            "El rol del profesor debe ser 'profesor'",
        )

    def test_02_rol_contacto_alumno(self):
        """El partner alumno debe tener rol_contacto = 'alumno'"""
        self.assertEqual(
            self.alumno1.rol_contacto,
            "alumno",
            "El rol del alumno debe ser 'alumno'",
        )

    def test_03_rol_default_es_alumno(self):
        """El rol por defecto debe ser 'alumno'"""
        partner = self.env["res.partner"].create({
            "name": "Sin Rol",
        })
        self.assertEqual(
            partner.rol_contacto,
            "alumno",
            "El rol por defecto debe ser 'alumno'",
        )

    # ---------------------------------------------------------
    # TEST 2: Verificar relación profesor <-> alumnos
    # ---------------------------------------------------------
    def test_04_profesor_tiene_alumnos(self):
        """El profesor debe tener 2 alumnos asociados"""
        self.assertEqual(
            len(self.profesor.alumno_ids),
            2,
            "El profesor debe tener 2 alumnos",
        )

    def test_05_alumno_tiene_profesor(self):
        """El alumno debe tener referencia a su profesor"""
        self.assertEqual(
            self.alumno1.profesor_id.id,
            self.profesor.id,
            "El alumno debe apuntar al profesor correcto",
        )

    def test_06_alumno_ids_contiene_ambos_alumnos(self):
        """alumno_ids del profesor debe contener los dos alumnos"""
        self.assertIn(self.alumno1, self.profesor.alumno_ids)
        self.assertIn(self.alumno2, self.profesor.alumno_ids)

    # ---------------------------------------------------------
    # TEST 3: Verificar compute alumno_user_ids
    # ---------------------------------------------------------
    def test_07_alumno_user_ids_sin_usuario(self):
        """Sin usuario vinculado, alumno_user_ids debe estar vacío"""
        self.assertFalse(
            self.profesor.alumno_user_ids,
            "Sin usuarios vinculados, alumno_user_ids debe estar vacío",
        )

    def test_08_alumno_user_ids_con_usuario(self):
        """Con usuario vinculado al alumno, debe aparecer en alumno_user_ids"""
        user = self.env["res.users"].create({
            "name": "Usuario Alumno",
            "login": "alumno_user_test_" + str(self.alumno1.id),
            "partner_id": self.alumno1.id,
            "groups_id": [(4, self.group_alumno.id)],
        })
        self.assertIn(
            user,
            self.profesor.alumno_user_ids,
            "El usuario alumno debe aparecer en alumno_user_ids del profesor",
        )

    # ---------------------------------------------------------
    # TEST 4: Verificar grupos de seguridad
    # ---------------------------------------------------------
    def test_09_grupo_alumno_existe(self):
        """El grupo Alumno debe existir"""
        self.assertTrue(
            self.group_alumno,
            "El grupo Aulavie / Alumno debe existir",
        )

    def test_10_grupo_profesor_existe(self):
        """El grupo Profesor debe existir"""
        self.assertTrue(
            self.group_profesor,
            "El grupo Aulavie / Profesor debe existir",
        )

    def test_11_grupo_profesor_implica_alumno(self):
        """El grupo Profesor debe implicar (heredar) el grupo Alumno"""
        self.assertIn(
            self.group_alumno,
            self.group_profesor.implied_ids,
            "El grupo Profesor debe incluir los permisos de Alumno",
        )

    # ---------------------------------------------------------
    # TEST 5: Verificar campo permitir_salir_redes_sociales
    # ---------------------------------------------------------
    def test_12_redes_sociales_default_false(self):
        """Por defecto permitir_salir_redes_sociales debe ser False"""
        partner = self.env["res.partner"].create({
            "name": "Test Redes",
        })
        self.assertFalse(
            partner.permitir_salir_redes_sociales,
            "Por defecto no debe permitir salir en redes sociales",
        )

    def test_13_redes_sociales_activar(self):
        """Se puede activar el campo permitir_salir_redes_sociales"""
        self.alumno1.write({"permitir_salir_redes_sociales": True})
        self.assertTrue(
            self.alumno1.permitir_salir_redes_sociales,
            "Debe permitir activar salir en redes sociales",
        )

    # ---------------------------------------------------------
    # TEST 6: Verificar dominio profesor_id
    # ---------------------------------------------------------
    def test_14_profesor_no_tiene_profesor_asignado(self):
        """Un contacto profesor no debe tener profesor_id asignado"""
        self.assertFalse(
            self.profesor.profesor_id,
            "Un profesor no debe tener un profesor asignado",
        )

    def test_15_cambio_rol_alumno_a_profesor(self):
        """Se puede cambiar el rol de alumno a profesor"""
        self.alumno2.write({
            "rol_contacto": "profesor",
            "profesor_id": False,
        })
        self.assertEqual(
            self.alumno2.rol_contacto,
            "profesor",
            "El cambio de rol a profesor debe guardarse correctamente",
        )
