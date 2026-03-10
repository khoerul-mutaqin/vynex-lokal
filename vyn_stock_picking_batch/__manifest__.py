{
    "name": "vyn_stock_picking_batch",
    "version": "18.0.0.0.0",
    "summary": "Customizations for stock picking batch",
    "description": """
        Customizations for the stock picking batch template view in Odoo.
    """,
    "author": "Vynex",
    "depends": ["product", "uom", "stock_picking_batch"],  # List of dependencies
    "data": [
        "views/vyn_stock_picking_batch_form.xml",
    ],
    "installable": True,
    "application": False,
}
