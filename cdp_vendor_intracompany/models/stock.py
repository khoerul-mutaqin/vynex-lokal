from odoo import models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round
import traceback
class StockMove(models.Model):
    _inherit = "stock.move"
    
class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Handle PO => Receipt QTY > DEMAND    
    def _cdp_update_move_qty(self):
        for picking in self:
            fields_sync = self.env["cdp.fields.sync"].sudo()
            origin = picking.purchase_id.origin
            if picking.picking_type_id.code == "incoming" and origin:
                sale_order = self.env["sale.order"]
                related_so = sale_order.sudo().search(
                    [
                        ("name", "=", origin),
                        ("state", "=", "sale"),
                    ]
                )
                if not related_so:
                    continue        
                all_do = related_so.mapped("picking_ids").filtered(
                    lambda x: x.state not in ["done", "cancel"]
                    and x.picking_type_id.code == "outgoing"
                )
                all_moves = all_do.mapped("move_ids_without_package")
                for current_move in self.move_ids_without_package:
                    for move in all_moves:
                        if current_move.product_id == move.product_id:
                            fields_sync.fal_run_sync_record(
                                "stock.move", "stock.move", current_move, move
                            )


    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            picking._cdp_update_move_qty()
            fields_sync = self.env["cdp.fields.sync"].sudo()
            sales = picking.sale_id
            if picking.picking_type_id.code == "outgoing" and sales.cdp_origin_order:
                sale_order = self.env["sale.order"]
                purchase_order = self.env["purchase.order"]
                intra_so = sale_order.sudo().search(
                    [
                        ("cdp_origin_order", "=", sales.cdp_origin_order),
                        ("state", "=", "sale"),
                    ]
                )
                intra_po = purchase_order.sudo().search(
                    [
                        ("cdp_origin_order", "=", sales.cdp_origin_order),
                        ("state", "=", "purchase"),
                    ]
                )
                all_do = intra_so.mapped("picking_ids").filtered(
                    lambda x: x.state not in ["done", "cancel"]
                    and x.picking_type_id.code != "outgoing"
                ) + intra_po.mapped("picking_ids").filtered(
                    lambda x: x.state not in ["done", "cancel"]
                    and x.picking_type_id.code != "incoming"
                )
                all_moves = all_do.mapped("move_ids_without_package")
                for current_move in self.move_ids_without_package:
                    for move in all_moves:
                        if current_move.product_id == move.product_id:
                            fields_sync.fal_run_sync_record(
                                "stock.move", "stock.move", current_move, move
                            )

                for do in all_do:
                    if picking.state == "done":
                        do.with_context(skip_sanity_check=True).button_validate()

                    moves = (
                        do.mapped("backorder_ids")
                        .filtered(lambda x: x.state != "done")
                        .mapped("move_ids_without_package")
                    )
                    for move in moves:
                        move.move_line_ids.unlink()
        return res
