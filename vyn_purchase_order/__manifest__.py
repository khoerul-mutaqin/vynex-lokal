{
    "name": "vyn_purchase_order",
    "version": "18.0.0.0.0",
    "summary": "Customizations for purchase order model",
    "description": """
        Customizations for the purchase order in Odoo.
    """,
    "author": "Vynex",
    "depends": ["purchase", "uom", "vyn_purchase_order_line", "fal_purchase_title"],
    "data": [
        "report/vyn_report_purchaseorder_weitai.xml",
        "views/vyn_purchase_order_form.xml",
        "views/vyn_purchase_order_tree.xml",
    ],
    "installable": True,
    "application": False,
}
