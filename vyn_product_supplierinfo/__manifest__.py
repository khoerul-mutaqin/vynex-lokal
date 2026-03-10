{
    "name": "vyn_product_supplierinfo",
    "version": "18.0.0.0.0",
    "summary": "Customizations for product supplierinfo model",
    "description": """
        Customizations for the product supplierinfo in Odoo.
    """,
    "author": "Vynex",
    "depends": ["product", "uom"],  # List of dependencies
    "data": [
        "views/vyn_product_supplierinfo_tree.xml",
    ],
    "installable": True,
    "application": False,
}
