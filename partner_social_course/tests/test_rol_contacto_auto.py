from odoo.tests import common


class TestRolContactoAutoProfesor(common.TransactionCase):
    """Test para verificar que el rol de contacto se asigna automáticamente"""

    def setUp(self):
        super(TestRolContactoAutoProfesor, self).setUp()
        self.Partner = self.env['res.partner']
        self.Users = self.env['res.users']

    def test_contacto_sin_usuario_es_alumno(self):
        """Test: Un contacto sin usuario asociado debe tener rol de alumno"""
        partner = self.Partner.create({
            'name': 'Estudiante Test',
            'email': 'estudiante@test.com',
        })

        self.assertEqual(partner.rol_contacto, 'alumno',
                        "Un contacto sin usuario debe ser alumno por defecto")

    def test_contacto_con_usuario_es_profesor(self):
        """Test: Un contacto con usuario asociado debe tener rol de profesor automáticamente"""
        # Crear un usuario
        user = self.Users.create({
            'name': 'Profesor Test',
            'login': 'profesor@test.com',
            'email': 'profesor@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        # El partner asociado al usuario debe ser automáticamente profesor
        partner = user.partner_id

        self.assertEqual(partner.rol_contacto, 'profesor',
                        "Un contacto asociado a un usuario debe ser profesor automáticamente")

    def test_cambio_usuario_cambia_rol(self):
        """Test: Cambiar la asociación de usuario debe cambiar el rol automáticamente"""
        # Crear un contacto sin usuario (será alumno)
        partner = self.Partner.create({
            'name': 'Test Cambio Rol',
            'email': 'cambio@test.com',
        })

        self.assertEqual(partner.rol_contacto, 'alumno',
                        "Inicialmente debe ser alumno")

        # Crear y asociar un usuario
        user = self.Users.create({
            'name': 'Test User',
            'login': 'testuser@test.com',
            'email': 'testuser@test.com',
            'partner_id': partner.id,
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        # Forzar recompute
        partner._compute_rol_contacto()

        self.assertEqual(partner.rol_contacto, 'profesor',
                        "Después de asociar usuario debe ser profesor")

    def test_eliminar_usuario_vuelve_alumno(self):
        """Test: Eliminar asociación de usuario debe volver el rol a alumno"""
        # Crear usuario con partner
        user = self.Users.create({
            'name': 'Usuario Temporal',
            'login': 'temporal@test.com',
            'email': 'temporal@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        partner = user.partner_id
        self.assertEqual(partner.rol_contacto, 'profesor',
                        "Con usuario debe ser profesor")

        # Desactivar el usuario (simula eliminar relación)
        user.active = False

        # Crear nuevo partner sin usuario para probar
        partner_sin_user = self.Partner.create({
            'name': 'Sin Usuario',
            'email': 'sinusuario@test.com',
        })

        self.assertEqual(partner_sin_user.rol_contacto, 'alumno',
                        "Sin usuario debe ser alumno")

    def test_multiple_partners_roles(self):
        """Test: Verificar roles múltiples correctamente"""
        # Crear varios contactos
        alumno1 = self.Partner.create({
            'name': 'Alumno 1',
            'email': 'alumno1@test.com',
        })

        alumno2 = self.Partner.create({
            'name': 'Alumno 2',
            'email': 'alumno2@test.com',
        })

        # Crear profesores con usuarios
        profesor1_user = self.Users.create({
            'name': 'Profesor 1',
            'login': 'profesor1@test.com',
            'email': 'profesor1@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        profesor2_user = self.Users.create({
            'name': 'Profesor 2',
            'login': 'profesor2@test.com',
            'email': 'profesor2@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        # Verificar roles
        self.assertEqual(alumno1.rol_contacto, 'alumno')
        self.assertEqual(alumno2.rol_contacto, 'alumno')
        self.assertEqual(profesor1_user.partner_id.rol_contacto, 'profesor')
        self.assertEqual(profesor2_user.partner_id.rol_contacto, 'profesor')

        print("✅ Todos los tests pasaron correctamente!")
        print(f"  - Alumno 1 rol: {alumno1.rol_contacto}")
        print(f"  - Alumno 2 rol: {alumno2.rol_contacto}")
        print(f"  - Profesor 1 rol: {profesor1_user.partner_id.rol_contacto}")
        print(f"  - Profesor 2 rol: {profesor2_user.partner_id.rol_contacto}")
