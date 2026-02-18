# -*- coding: utf-8 -*-
{
    'name': 'Grupos Aulavie',
    'version': '1.0',
    'category': 'Contactos',
    'summary': 'Gestión de grupos de contactos',
    'description': """
        Módulo para gestionar grupos de contactos.
        Permite crear grupos con día de la semana y hora.
    """,
    'author': 'Alvaro(Xtendoo)',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/aulavie_days_data.xml',
        'views/aulavie_groups_views.xml',
        'views/aulavie_sesiones_views.xml',
        'views/aulavie_groups_menu.xml',
    ],
    'installable': True,
    'application': False,
}
