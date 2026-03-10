from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MRP(models.Model):
    _inherit = 'mrp.production'

    cdp_origin_order = fields.Char("Origin Order", copy=False)

    def action_confirm(self):
        res = super(MRP, self).action_confirm()
        for mrp in self:
            for move in mrp.move_raw_ids:
                routes = move.product_id.route_ids.ids
                if any(r in [1, 7] for r in routes):
                    move._run_procurement()
                    try:          
                        _logger.info("Procurement launched for %s", move.product_id.display_name)
                    except Exception as e:
                        _logger.info("Procurement failed for %s: %s", move.product_id.display_name, e)
        #write PO quantity 
        po_lines = self.env["purchase.order.line"].search([("state", "=", "draft"), ("move_dest_ids", "in", mrp.move_raw_ids.ids)])
        for line in po_lines:
            qty_pc = sum(
                line.move_dest_ids.mapped(
                    lambda m: m.product_uom._compute_quantity(
                        qty=m.product_uom_qty,
                        to_unit=line.product_id.uom_id,
                    )
                )
            )

            qty_po = line.product_id.uom_id._compute_quantity(
                qty=qty_pc,
                to_unit=line.product_uom,
            )

            line.write({'product_qty': qty_po})
        return res
        