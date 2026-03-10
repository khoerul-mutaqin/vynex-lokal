from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cdp_origin_order = fields.Char("Origin Order", copy=False)

    def inter_company_create_sale_order(self, company):
        sale_orders = (
            self.env["sale.order"]
            .sudo()
            .search([("auto_purchase_order_id", "=", self.id)])
        )
        if sale_orders:
            return True
        return super(PurchaseOrder, self).inter_company_create_sale_order(company)

    def _cdp_update_move_dest_ids(self, so):
        finished_move = []
        picking_move = False
        move_and_move = {}
        if so.picking_ids and self.picking_ids:
            for picking in so.picking_ids:
                picking_move = picking.move_ids_without_package

            for picking in self.picking_ids:
                finished_move.append(picking.move_ids_without_package)

            for finished in finished_move:
                for pm in picking_move:
                    if finished.product_id == pm.product_id:
                        move_and_move[finished] = pm

            for fin_move, pick_move in move_and_move.items():
                fin_move.move_dest_ids = [(6, 0, pick_move.ids)]

    def button_confirm(self):
        res = super().button_confirm()
        for po in self:
            po._cdp_update_move_dest_ids(po.fal_all_recorded_sale)
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _create_or_update_picking(self):
        return True
    