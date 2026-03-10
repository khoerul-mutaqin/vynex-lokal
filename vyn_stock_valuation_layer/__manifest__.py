{
    "name": "vyn_stock_valuation_layer",
    "version": "18.0.0.0.0",
    "summary": "Customizations for stock valuation layer model",
    "description": """
        Customizations for the stock valuation layer in Odoo.
    """,
    "author": "Vynex",
    "depends": ["stock", "uom"],  # List of dependencies
    "data": [
        "views/vyn_stock_valuation_layer_tree.xml",
    ],
    "installable": True,
    "application": False,
}
