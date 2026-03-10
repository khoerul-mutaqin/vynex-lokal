{
    "name": "vyn_stock_picking",
    "version": "18.0.0.0.0",
    "summary": "Customizations for Stock picking Model",
    "description": """
        Customizations for the stok picking model in Odoo.
    """,
    "author": "Vynex",
    "depends": ["stock_picking_batch", "uom", "vyn_product_template"],  # List of dependencies
    "data": [
        "views/vyn_stock_picking_search.xml",
        "views/vyn_stock_picking_form.xml",
        "views/vyn_stock_picking_tree.xml",
    ],
    "installable": True,
    "application": False,
}
