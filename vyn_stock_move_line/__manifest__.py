{
    "name": "vyn_stock_move_line",
    "version": "18.0.0.0.0",
    "summary": "Customizations for stock move line",
    "description": """
        Customizations for the stock move line in Odoo.
    """,
    "author": "Vynex",
    "depends": ["stock", "uom"],  # List of dependencies
    "data": [
        "views/vyn_stock_move_line_tree.xml",
    ],
    "installable": True,
    "application": False,
}
