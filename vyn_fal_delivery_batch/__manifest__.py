{
    "name": "vyn_fal_delivery_batch",
    "version": "18.0.0.0.0",
    "summary": "Customizations for fal delivery batch model",
    "description": """
        Customizations for the fal delivery batch in Odoo.
    """,
    "author": "Vynex",
    "depends": [
        "product",
        "uom",
        "stock",
        "vyn_fal_delivery_batch_line",
    ],  # List of dependencies
    # dépends du module vyn_fal_delivery_batch_line impérativement
    "data": [
        "views/vyn_fal_delivery_batch_form.xml",
    ],
    "installable": True,
    "application": False,
}
