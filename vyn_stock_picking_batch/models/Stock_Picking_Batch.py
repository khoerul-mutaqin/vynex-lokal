from odoo import models, fields


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"
