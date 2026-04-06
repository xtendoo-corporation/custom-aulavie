{
    "name": "Partner Social Course",
    "version": "19.0.1.0.0",
    "summary": "Extiende contactos con permiso de redes sociales y cursos",
    "category": "Contacts",
    "author": "Custom Aulavie",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "hr_attendance", "aulavie_groups"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "application": False,
}

