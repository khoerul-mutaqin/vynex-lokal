from odoo import models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round
import traceback
class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _action_assign(self, force_qty=False):
        res = super(StockMove, self)._action_assign(force_qty=force_qty)      
        for rec in self.filtered(lambda m: m.move_dest_ids):
            qty = rec.update_get_qty(rec.quantity)
            if qty != rec.quantity and rec.quantity != 0:
                rec['quantity'] = qty
        return res
    
    # handle single create
    def update_get_qty(self, quantity=None):
        all_do = self.move_orig_ids.filtered(lambda m: m.state == "done")
        total_qty = sum(all_do.move_line_ids.mapped("quantity"))
        total_reserved = 0
        picking = self.picking_id.backorder_id

        while picking:
            total_reserved += sum(
                picking.move_ids.filtered(
                    lambda m: m.product_id == self.product_id and m.state == "done"
                ).move_line_ids.mapped("quantity")
            )
            picking = picking.backorder_id

        available_qty = total_qty - total_reserved

        return available_qty if quantity != available_qty else quantity
    
    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        quantity = self.update_get_qty(quantity=quantity) or quantity
        result = super()._prepare_move_line_vals(quantity=quantity,reserved_quant=reserved_quant)
        return result
    
class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _cdp_update_move_qty(self):
        for rec in self:
            all_do = rec.filtered(
                lambda x: x.state not in ["done", "cancel"]
                and x.picking_type_id.code == "incoming"
            )
            stock_move_ids = all_do.group_id.stock_move_ids 
            for current_move in all_do.move_ids_without_package:
                for move in stock_move_ids:
                    if current_move.product_id == move.product_id and current_move.quantity > move.product_uom_qty and move.state != 'done':
                        move.write({
                            "product_uom_qty": current_move.quantity,
                        })
                        for ml in move.move_line_ids:
                            ml.quantity = current_move.quantity                        


    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
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
                )
                all_moves = all_do.mapped("move_ids_without_package")
                # for current_move in self.move_ids_without_package:
                #     for move in all_moves:
                #         if current_move.product_id == move.product_id:
                #             fields_sync.fal_run_sync_record(
                #                 "stock.move", "stock.move", current_move, move
                #             )

                for do in all_do:
                    # if picking.state == "done":
                        # do.with_context(skip_sanity_check=True).button_validate()

                    moves = (
                        do.mapped("backorder_ids")
                        .filtered(lambda x: x.state != "done")
                        .mapped("move_ids_without_package")
                    )
                    for move in moves:
                        move.move_line_ids.unlink()
        return res
