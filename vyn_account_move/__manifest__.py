{
    "name": "vyn_account_move",
    "version": "18.0.0.0.0",
    "summary": "Customizations for account move",
    "description": """
        Customizations for the account move in Odoo.
    """,
    "author": "Vynex",
    "depends": ["account", "uom", "fal_invoice_title"],  # List of dependencies
    "data": [
        "views/vyn_account_move_form.xml",
    ],
    "installable": True,
    "application": False,
}
