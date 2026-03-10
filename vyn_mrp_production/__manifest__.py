{
    "name": "vyn_mrp_production",
    "version": "18.0.0.0.0",
    "summary": "Customizations for mrp production",
    "description": """
        Customizations for the mrp production in Odoo.
    """,
    "author": "Vynex",
    "depends": [
        "mrp",
        "uom",
        "stock",
        "sale",
        "account",
        "purchase",
        "fal_sale_title",
        "vyn_product_template",
        "vyn_stock_move",
    ],
    "data": [
        "views/vyn_mrp_production_form.xml",
        "views/vyn_mrp_production_tree.xml",
        "report/report_mrporder_weitai.xml",
    ],
    "installable": True,
    "application": False,
}
