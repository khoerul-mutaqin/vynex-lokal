{
    "name": "vyn_product_category",
    "version": "18.0.0.0.0",
    "summary": "Customizations for product category model",
    "description": """
        Customizations for the product category in Odoo.
    """,
    "author": "Vynex",
    "depends": ["product", "uom", "fal_sale_purchase_no_grouping"],  # List of dependencies
    "data": [
        "views/vyn_product_category_tree.xml",
    ],
    "installable": True,
    "application": False,
}
