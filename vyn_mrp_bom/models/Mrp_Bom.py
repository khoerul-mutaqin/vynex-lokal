from odoo import models, fields


class vyn_mrp_bom(models.Model):
    _inherit = "mrp.bom"

    vyn_product_category = fields.Char(
        string="Product category",
        store=True,
        readonly=True,
        index=True,
        related="product_tmpl_id.categ_id.display_name",
    )
    vyn_rfrence_interne = fields.Char(
        string="Référence interne",
        store=True,
        readonly=True,
        related="product_tmpl_id.default_code",
    )
