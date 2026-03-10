from odoo import models, fields


class FalDeliveryBatchLine(models.Model):
    _inherit = "fal.delivery.batch.line"

    vyn_customer_order = fields.Char(
        string="Customer Order",
        store=True,
        readonly=True,
        related="invoice_line_id.sale_line_ids.order_id.fal_title",
    )
