from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    vyn_source_qty = fields.Many2one(
        "stock.quant", string="Source Qty", compute="_compute_source_qty"
    )

    @api.depends("location_id", "product_id")
    def _compute_source_qty(self):
        for record in self:
            if record.location_id.quant_ids:
                for line in record.location_id.quant_ids:
                    if line.product_id == record.product_id:
                        record.vyn_source_qty = line.id
                    else:
                        record.vyn_source_qty = None

    vyn_stock = fields.Float(
        string="Stock", readonly=True, related="vyn_source_qty.quantity"
    )
