{
    "name": "vyn_ir_model_data",
    "version": "18.0.0.0.0",
    "summary": "Customizations for ir model data model",
    "description": """
        Customizations for the ir model data in Odoo.
    """,
    "author": "Vynex",
    "depends": ["base"],  # List of dependencies
    "data": [
        "views/vyn_ir_model_data_tree.xml",
        "views/vyn_ir_model_data_search.xml",
    ],
    "installable": True,
    "application": False,
}
