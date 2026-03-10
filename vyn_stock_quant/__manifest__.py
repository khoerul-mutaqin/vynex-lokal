{
    "name": "vyn_stock_quant",
    "version": "18.0.0.0.0",
    "summary": "Customizations for stock quant model",
    "description": """
        Customizations for the stock quant in Odoo.
    """,
    "author": "Vynex",
    "depends": ["stock", "uom"],  # List of dependencies
    "data": [
        "views/vyn_stock_quant_search.xml",
        "views/vyn_stock_quant_tree.xml",
    ],
    "installable": True,
    "application": False,
}
