from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    vyn_move_line_note = fields.Html(
        string="Move line note", readonly=True, store=True, related="picking_id.note"
    )
    vyn_customer_order_number = fields.Char(
        string="Customer order number", readonly=True, store=True
    )
    vyn_not_received = fields.Float(
        string="Not received",
        required=True,
        readonly=True,
        compute="_compute_not_received",
    )
    vyn_demand = fields.Float(
        string="Demand", store=True, readonly=True, related="move_id.product_uom_qty"
    )

    @api.depends("vyn_demand", "quantity")
    def _compute_not_received(self):
        for record in self:
            record.vyn_not_received = record.vyn_demand - record.quantity

