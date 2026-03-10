{
    "name": "vyn_mrp_bom",
    "version": "18.0.0.0.0",
    "summary": "Customizations for mrp bom",
    "description": """
        Customizations for the mrp bom in Odoo.
    """,
    "author": "Vynex",
    "depends": ["mrp", "uom", "stock"],
    "data": [
        "views/vyn_mrp_bom_select.xml",
        "views/vyn_mrp_bom_tree.xml",
        "views/vyn_mrp_bom_form.xml",
    ],
    "installable": True,
    "application": False,
}
