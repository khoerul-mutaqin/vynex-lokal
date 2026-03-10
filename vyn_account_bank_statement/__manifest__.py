{
    "name": "vyn_account_bank_statement",
    "version": "18.0.0.0.0",
    "summary": "Customizations for account bank statement",
    "description": """
        Customizations for the account bank statement in Odoo.
    """,
    "author": "Vynex",
    "depends": ["account", "uom"],  # List of dependencies
    "data": [
        "views/vyn_account_bank_statement_tree.xml",
    ],
    "installable": True,
    "application": False,
}
