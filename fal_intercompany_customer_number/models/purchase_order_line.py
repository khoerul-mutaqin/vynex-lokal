from odoo import models, api, fields, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    fal_customer_invoice_number = fields.Char(string="Customer Invoice Number", copy=False)
