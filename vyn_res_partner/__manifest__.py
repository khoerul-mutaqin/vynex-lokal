{
    "name": "vyn_res_partner",
    "version": "18.0.0.0.0",
    "summary": "Customizations for res partner model",
    "description": """
        Customizations for res partner in Odoo.
    """,
    "author": "Vynex",
    "depends": ["fal_partner_short_name"],  # List of dependencies
    "data": [
        "views/vyn_res_partner_form.xml",
        "views/vyn_res_partner_tree.xml",
    ],
    "installable": True,
    "application": False,
}
