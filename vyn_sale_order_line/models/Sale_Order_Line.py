from odoo import models, fields, api
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    vyn_actual_cny_rate = fields.Float(string='Actual CNY rate',readonly=True,related="currency_id.rate")