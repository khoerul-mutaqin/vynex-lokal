{
    "name": "vyn_account_move_line",
    "version": "18.0.0.0.0",
    "summary": "Customizations for account move line",
    "description": """
        Customizations for the account move line in Odoo.
    """,
    "author": "Vynex",
    "depends": ["account", "uom"],  # List of dependencies
    "data": [
        "views/vyn_account_move_line_search.xml",
    ],
    "installable": True,
    "application": False,
}
