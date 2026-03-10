{
    "name": "vyn_product_template",
    "version": "18.0.0.0.0",
    "summary": "Customizations for Product Template",
    "description": """
        Customizations for the product template in Odoo.
    """,
    "author": "Vynex",
    "depends": ["product", "uom"],  # List of dependencies
    "data": [
        "views/vyn_product_template_product_tree.xml",
        "views/vyn_product_template_product_form.xml",
        "views/vyn_product_template_search.xml",
    ],
    "installable": True,
    "application": False,
}
