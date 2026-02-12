{
    "name": "Controle de Combustível",
    "version": "1.1.0",
    "summary": "Abastecimentos + Tanque 6000L + Permissões",
    "category": "Fleet",
    "author": "Alan Maia",
    "license": "LGPL-3",
    "depends": ["base", "fleet"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/fuel_tank_data.xml",
        "views/fuel_tank_views.xml",
        "views/fuel_stock_move_views.xml",
        "views/fuel_log_views.xml",
    ],
    "installable": True,
    "application": True,
}
