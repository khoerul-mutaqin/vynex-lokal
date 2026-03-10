{
    "name": "vyn_account_account",
    "version": "18.0.0.0.0",
    "summary": "Customizations for account account",
    "description": """
        Customizations for the account account in Odoo.
    """,
    "author": "Vynex",
    "depends": ["account", "uom"],  # List of dependencies
    "data": [
        "views/vyn_account_account_tree.xml",
    ],
    "installable": True,
    "application": False,
}
