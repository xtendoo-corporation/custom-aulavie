{
    "name": "Partner Social Course",
    "version": "19.0.1.1.0",
    "summary": "Extiende contactos con permiso de redes sociales, cursos y rol profesor/alumno",
    "category": "Contacts",
    "author": "Custom Aulavie",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "aulavie_groups"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "wizard/import_alumnos_wizard_views.xml",
        "views/res_partner_views.xml",
        "views/aulavie_groups_views.xml",
        "views/menus.xml",
        "data/nivel_escolar_data.xml",
    ],
    "demo": [
        "data/demo_users.xml",
    ],
    "installable": True,
    "application": False,
}

