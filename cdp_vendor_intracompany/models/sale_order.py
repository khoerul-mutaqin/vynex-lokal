from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    cdp_origin_order = fields.Char("Origin Order")
    cdp_created_intra_company = fields.Boolean(default=False, copy=False)

    def _cdp_update_move_dest_ids(self, so):
        finished_move = []
        picking_move = False
        move_and_move = {}
        if so.mrp_production_ids and so.picking_ids:
            for picking in so.picking_ids:
                picking_move = picking.move_ids_without_package
            for mrp in so.mrp_production_ids:
                if not mrp.move_dest_ids and mrp.move_finished_ids:
                    finished_move.append(mrp.move_finished_ids)

            for finished in finished_move:
                for pm in picking_move:
                    if finished.product_id == pm.product_id:
                        move_and_move[finished] = pm

            for fin_move, pick_move in move_and_move.items():
                fin_move.move_dest_ids = [(6, 0, pick_move.ids)]

                

    def action_confirm(self):
        for rec in self:
            # why need to set draft and call generate_action_launch_stock
            # rec.write({"state": "draft"})
            # rec.sudo().generate_action_launch_stock()
            rec.sudo().button_upd_values_po_line()
        return super(SaleOrder, self).action_confirm()

    def fal_action_confirm(self):
        res = super(SaleOrder, self).fal_action_confirm()
        if self.cdp_origin_order == self.name:
            sale_order = self.env["sale.order"]
            purchase_order = self.env["purchase.order"]
            intra_so = sale_order.sudo().search(
                [
                    ("cdp_origin_order", "=", self.cdp_origin_order),
                    ("state", "in", ["draft", "sent"]),
                ]
            )
            intra_po = purchase_order.sudo().search(
                [
                    ("cdp_origin_order", "=", self.cdp_origin_order),
                    ("state", "=", "draft"),
                ]
            )
            for so in self:
                if self.cdp_origin_order:
                    for so in intra_so:
                        if so.state != "sale":
                            so.fal_action_confirm()
                            so.button_upd_values_po_line()
                            self._cdp_update_move_dest_ids(so)
                            if so.mrp_production_ids:
                                for mrp in so.mrp_production_ids:
                                    mrp.with_company(mrp.company_id).action_confirm()
                    for po in intra_po:
                        if po.company_id.id != 1 and po.state != "purchase":
                            po.button_confirm()

        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        cancel_warning = self._show_cancel_wizard()
        if cancel_warning:
            return res
        else:
            if self.cdp_origin_order == self.name:
                self.is_confirmed = False
                sale_order = self.env["sale.order"]
                purchase_order = self.env["purchase.order"]
                intra_so = sale_order.sudo().search(
                    [
                        ("cdp_origin_order", "=", self.cdp_origin_order),
                        ("state", "in", ["sale"]),
                    ]
                )
                intra_po = purchase_order.sudo().search(
                    [
                        ("cdp_origin_order", "=", self.cdp_origin_order),
                        ("state", "=", "purchase"),
                    ]
                )
                for so in self:
                    if self.cdp_origin_order:
                        for so in intra_so:
                            if so.state == "sale":
                                so.action_cancel()

                        for po in intra_po:
                            if po.state == "purchase":
                                po.button_cancel()
        return res

    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        if self.cdp_origin_order == self.name:
            sale_order = self.env["sale.order"]
            purchase_order = self.env["purchase.order"]
            intra_so = sale_order.sudo().search(
                [
                    ("cdp_origin_order", "=", self.cdp_origin_order),
                    ("state", "in", ["cancel"]),
                ]
            )
            intra_po = purchase_order.sudo().search(
                [
                    ("cdp_origin_order", "=", self.cdp_origin_order),
                    ("state", "in", ["cancel"]),
                ]
            )
            for so in self:
                if self.cdp_origin_order:
                    for so in intra_so:
                        if so.state == "cancel":
                            so.action_draft()

                    for po in intra_po:
                        if po.state == "cancel":
                            po.button_draft()
        return res

    def button_upd_values_po_line(self):
        purchase_orders = self.env["purchase.order"].search(
            [("origin", "ilike", self.name), ("state", "!=", "cancel")]
        )
        if purchase_orders:
            today = fields.Date.today()
            for po in purchase_orders:
                for line in po.order_line:
                    sellers = line.product_id.seller_ids.filtered(
                        lambda s: s.partner_id.id == po.partner_id.id
                        and (not s.date_start or s.date_start <= today)
                        and (not s.date_end or s.date_end >= today)
                    )
                    sellers = sellers.sorted(
                        lambda s: (s.date_end or today, s.id), reverse=True
                    )

                    seller = sellers.filtered(
                        lambda s: s.min_qty == 0.0 or s.min_qty <= line.product_qty
                    )[:1]

                    if seller:
                        if po.currency_id != seller.currency_id:
                            po.write({"currency_id": seller.currency_id.id})

                        line.write(
                            {
                                "price_unit": seller.price,
                            }
                        )

    def action_generate_intra_company(self):
        for sale in self:
            if sale.state == "draft":
                sale.sudo().generate_action_launch_stock()

            sale.sudo().generate_intercompany_chain()

    def generate_intercompany_chain(self):
        self.cdp_created_intra_company = True
        sale_order = self.env["sale.order"]
        purchase_order = self.env["purchase.order"]
        mrp_production = self.env["mrp.production"]

        queue = [self]
        while queue:
            current_so = queue.pop(0)
            if current_so.state == "draft":
                current_so.cdp_origin_order = self.name
                current_so.cdp_created_intra_company = True
                current_so.sudo().generate_action_launch_stock()
                current_so.sudo().button_upd_values_po_line()


            pos = purchase_order.sudo().search(
                [("origin", "ilike", current_so.name), ("state", "!=", "cancel")]
            )

            for po in pos:
                if po.state in ["draft", "sent"]:
                    po.cdp_origin_order = self.name
                    po.sudo().generate_action_create_picking()

                so_created = sale_order.sudo().search(
                    [("client_order_ref", "ilike", po.name), ("state", "in", ["draft"])]
                )
                queue.extend(so_created)
            mrp = mrp_production.sudo().search(
                [("origin", "ilike", current_so.name), ("state", "in", ["draft"])]
            )
            mrp.cdp_origin_order = self.name
        

    def cdp_update_intra_company(self):
        cdp_origin = self.cdp_origin_order
        fields_sync = self.env["cdp.fields.sync"].sudo()

        sale_orders = (
            self.env["sale.order"]
            .sudo()
            .search([("cdp_origin_order", "ilike", cdp_origin)])
        )
        purchase_orders = (
            self.env["purchase.order"]
            .sudo()
            .search([("cdp_origin_order", "ilike", cdp_origin)])
        )
        mrp_productions = (
            self.env["mrp.production"]
            .sudo()
            .search([("cdp_origin_order", "ilike", cdp_origin)])
        )

        # --- Sync Purchase Orders ---
        for po in purchase_orders:
            for sol in self.order_line.sudo():

                pol = po.order_line.filtered(
                    lambda l: l.product_id.id == sol.product_id.id
                    and l.name == sol.name
                )
                if pol:

                    original_price = pol[0].price_unit
                    fields_sync.fal_run_sync_record(
                        "sale.order.line", "purchase.order.line", sol, pol[0]
                    )
                    pol[0].sudo().write({"price_unit": original_price})

                else:
                    line_data = sol.order_id._prepare_purchase_order_line_data(
                        sol, sol.order_id.date_order, po.company_id
                    )
                    line_data.update({"price_unit": sol.price_unit, "order_id": po.id})

                    self.env["purchase.order.line"].sudo().create(line_data)
            fields_sync.fal_run_sync_record("sale.order", "purchase.order", self, po)

        # --- Sync Sale Orders ---
        for so in sale_orders:
            for sol in self.order_line.sudo():

                sol_2 = so.order_line.filtered(
                    lambda l: l.product_id.id == sol.product_id.id
                    and l.name == sol.name
                )
                if sol_2:

                    original_price = sol_2[0].price_unit
                    fields_sync.fal_run_sync_record(
                        "sale.order.line", "sale.order.line", sol, sol_2[0]
                    )
                    sol_2[0].sudo().write({"price_unit": original_price})

                else:
                    line_data = {
                        "name": sol.name,
                        "product_uom_qty": sol.product_uom_qty,
                        "product_id": sol.product_id.id if sol.product_id else False,
                        "product_uom": (
                            sol.product_id.uom_id.id
                            if sol.product_id
                            else sol.product_uom.id
                        ),
                        "company_id": so.company_id.id,
                        "display_type": sol.display_type,
                        "order_id": so.id,
                        "price_unit": sol.price_unit,
                    }
                    self.env["sale.order.line"].sudo().create(line_data)
            fields_sync.fal_run_sync_record("sale.order", "sale.order", self, so)

        # --- Sync MRP & Stock Moves ---
        for sol in self.order_line.sudo():
            mrp = mrp_productions.filtered(
                lambda x: x.product_id.id == sol.product_id.id
            )
            if mrp:

                fields_sync.fal_run_sync_record(
                    "sale.order.line", "mrp.production", sol, mrp[0]
                )
                fields_sync.fal_run_sync_record(
                    "mrp.production",
                    "fal.production.order",
                    mrp[0],
                    mrp[0].fal_parent_or_prod_order_id,
                )

            for so in sale_orders:
                for move in so.picking_ids.mapped("move_ids_without_package"):
                    if move.product_id.id == sol.product_id.id:

                        fields_sync.fal_run_sync_record(
                            "sale.order.line", "stock.move", sol, move
                        )
                        self._cdp_update_move_dest_ids(so)

            for po in purchase_orders:
                for move in po.picking_ids.mapped("move_ids_without_package"):
                    if move.product_id.id == sol.product_id.id:

                        fields_sync.fal_run_sync_record(
                            "sale.order.line", "stock.move", sol, move
                        )
