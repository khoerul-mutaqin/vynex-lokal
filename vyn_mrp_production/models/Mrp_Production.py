from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    vyn_customer_order_number = fields.Char(
        string="Customer Order Number",
        store=True,
        readonly=True,
        related="procurement_group_id.sale_id.fal_title",
    )
    vyn_contained_qty_in_pack_1 = fields.Float(
        string="Contained Qty in Pack 1",
        readonly=True,
        related="product_id.vyn_uc_per_unit",
    )
    vyn_availability_component = fields.Char(
        string="Availability component",
        store=True,
        readonly=True,
        related="procurement_group_id.mrp_production_ids.components_availability",
    )
