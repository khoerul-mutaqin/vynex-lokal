from odoo import models
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        for line in self:
            sale_order = line.order_id
            origin_name = sale_order.name

            existing_po = self.env['purchase.order'].sudo().search([
                ('origin', 'ilike', origin_name),
                ('state', 'in', ['draft', 'sent', 'purchase'])
            ], limit=1)

            existing_mo = self.env['mrp.production'].sudo().search([
                ('origin', '=', origin_name),
                ('state', 'not in', ['cancel', 'done'])
            ], limit=1)

            if existing_po or existing_mo:
                continue

            super(SaleOrderLine, line)._action_launch_stock_rule(
                previous_product_uom_qty={line.id: previous_product_uom_qty.get(line.id)} if previous_product_uom_qty else False
            )
