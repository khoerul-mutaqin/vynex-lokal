from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"
    vyn_customer_order_number = fields.Char(
        string="Customer order number", store="True", readonly=True
    )
    vyn_product_to_produce = fields.Char(
        string="Product to produce",
        store="True",
        readonly=True,
        translate=True,
        related="group_id.mrp_production_ids.product_id.vyn_ancien_code",
    )
    vyn_quantity_to_produce = fields.Float(
        string="Quantity to produce",
        store="True",
        readonly=True,
        related="group_id.mrp_production_ids.product_qty",
    )
    vyn_product = fields.Char(
        string="Product", store="True", readonly=True, related="product_id.default_code"
    )
    vyn_related_field_supplier = fields.Char(
        string="Supplier",
        store="True",
        readonly=True,
        related="partner_id.display_name",
    )
