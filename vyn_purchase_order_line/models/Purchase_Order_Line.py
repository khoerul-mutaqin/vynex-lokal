from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    vyn_forecast_1 = fields.Float(string="Forecast", store=True)
    vyn_moq = fields.Float(string="MOQ", store=True)
    vyn_subtotal_vat = fields.Monetary(
        string="Subtotal VAT",
        currency_field="currency_id",
        compute="_compute_subtotal",
        store=True,
    )
    vyn_stock = fields.Float(
        string="Stock", readonly=True, related="product_id.qty_available"
    )

    @api.depends("product_qty", "price_unit")
    def _compute_subtotal(self):
        for record in self:
            record.vyn_subtotal_vat = record.product_qty * record.price_unit
