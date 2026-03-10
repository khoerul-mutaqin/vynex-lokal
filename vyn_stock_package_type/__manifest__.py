{
    "name": "vyn_stock_package_type",
    "version": "18.0.0.0.0",
    "summary": "Customizations for stock picking batch",
    "description": """
        Customizations for the stock picking batch template view in Odoo.
    """,
    "author": "Vynex",
    "depends": ["product", "uom", "stock"],  # List of dependencies
    "data": [
        "views/vyn_stock_package_type_tree.xml",
    ],
    "installable": True,
    "application": False,
}
