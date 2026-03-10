{
    "name": "vyn_sale_order",
    "version": "18.0.0.0.0",
    "summary": "Customizations for sale order template",
    "description": """
        Customizations for the sale order template view in Odoo.
    """,
    "author": "Vynex",
    "depends": ["sale_margin", "uom", "vyn_sale_order_line", "fal_sale_title"],
    "data": [
        "views/vyn_sale_order_tree.xml",
        "views/vyn_sale_order_form.xml",
    ],
    "installable": True,
    "application": False,
}
