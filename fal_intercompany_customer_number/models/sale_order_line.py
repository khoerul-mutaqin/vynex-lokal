from odoo import models, api, fields, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fal_customer_invoice_number = fields.Char(string="Customer Invoice Number", copy=False)
    