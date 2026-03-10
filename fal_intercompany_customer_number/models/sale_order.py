from odoo import models, api, fields, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fal_customer_number = fields.Char(string="Customer Number", copy=False)
