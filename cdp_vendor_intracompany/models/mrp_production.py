from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MRP(models.Model):
    _inherit = "mrp.production"

    cdp_origin_order = fields.Char("Origin Order", copy=False)

    def button_mark_done(self):
        res = super(MRP, self).button_mark_done()
        # sync When produce quantity more than original quantity
        for mrp in self:
            if mrp.move_finished_ids and mrp.origin:
                fields_sync = self.env["cdp.fields.sync"].sudo()
                sale_order = self.env["sale.order"].sudo()
                intra_so = sale_order.sudo().search(
                    [
                        ("name", "=", mrp.origin),
                        ("state", "=", "sale"),
                    ]
                )
                if intra_so:
                    all_do = intra_so.mapped("picking_ids").filtered(
                        lambda x: (
                            x.state not in ["done", "cancel"]
                            and x.picking_type_id.code == "outgoing"
                        )
                    )
                    all_moves = all_do.mapped("move_ids_without_package")
                    for current_move in self.move_finished_ids:
                        for move in all_moves:
                            if current_move.product_id == move.product_id:
                                fields_sync.fal_run_sync_record(
                                    "stock.move", "stock.move", current_move, move
                                )

        return res

    def action_confirm(self):
        res = super(MRP, self).action_confirm()
        for mrp in self:
            for move in mrp.move_raw_ids:
                routes = move.product_id.route_ids.ids
                if any(r in [1, 7] for r in routes):
                    move._run_procurement()
                    try:
                        _logger.info(
                            "Procurement launched for %s", move.product_id.display_name
                        )
                    except Exception as e:
                        _logger.info(
                            "Procurement failed for %s: %s",
                            move.product_id.display_name,
                            e,
                        )
        # write PO quantity
        po_lines = self.env["purchase.order.line"].search(
            [("state", "=", "draft"), ("move_dest_ids", "in", mrp.move_raw_ids.ids)]
        )
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

            line.write({"product_qty": qty_po})
        return res
