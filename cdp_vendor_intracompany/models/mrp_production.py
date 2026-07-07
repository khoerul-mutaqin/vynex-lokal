from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MRP(models.Model):
    _inherit = 'mrp.production'

    cdp_origin_order = fields.Char("Origin Order", copy=False)

    def write(self, vals):
        res = super().write(vals)

        if "state" in vals:
            for production in self:
                if production.qty_producing > production.product_qty:
                    production._cdp_update_move_qty()
        return res

    def _cdp_update_move_qty(self):
        for production in self:
            qty = production.qty_producing  
            # Update MO Qty
            # Finished Move
            finished_moves = production.move_finished_ids.filtered(
                lambda m: m.product_id == production.product_id
            )

            if not finished_moves:
                continue

            if production.state == "done":
                finished_moves.write({
                    "quantity": qty,
                })
            # Finished Move Lines
            for ml in production.finished_move_line_ids.filtered(
                lambda ml: ml.product_id == production.product_id
            ):
                ml.quantity = qty

            # Delivery Move
            delivery_moves = finished_moves.mapped("move_dest_ids").filtered(
                lambda m: m.state not in ("done", "cancel")
            )

            for move in delivery_moves:
                for ml in move.move_line_ids:
                    ml.quantity = qty

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
        