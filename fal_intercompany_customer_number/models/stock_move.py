from odoo import models, api, fields, _
import re


class StockMove(models.Model):
    _inherit = "stock.move"

    fal_customer_invoice_number = fields.Char(string="Customer Invoice Number")

    def write(self, vals):
        res = super().write(vals)

        if self.env.context.get("skip_sync"):
            return res

        for move in self:
            if vals.get("fal_customer_invoice_number") and move.picking_id:
                picking = move.picking_id
                new_invoice = vals["fal_customer_invoice_number"]

                # ⛔ Skip update fal_customer_number jika picking sudah done
                if picking.state != "done":
                    existing_raw = picking.fal_customer_number or ""
                    existing_items = [x.strip() for x in existing_raw.split(",") if x.strip()]
                    new_items = [x.strip() for x in new_invoice.split(",") if x.strip()]
                    filtered_new = [item for item in new_items if item not in existing_items]

                    if filtered_new:
                        combined = ", ".join(existing_items + filtered_new)
                        picking.with_context(skip_sync=True).write({
                            "fal_customer_number": combined
                        })

                        # 🔁 Propagasi fal_customer_number ke dokumen lain
                        origin_parts = re.split(r"\s*[-,]\s*", picking.origin or "")
                        visited = set()
                        for origin_code in origin_parts:
                            if origin_code.strip():
                                picking._recursive_propagate_customer_number(
                                    origin_code.strip(), combined, visited
                                )

                # ✅ Untuk stock.move: hanya update sekali saja jika masih kosong
                if not move.fal_customer_invoice_number:
                    move.with_context(skip_sync=True).write({
                        "fal_customer_invoice_number": new_invoice
                    })

                # ✅ Untuk sale_line_id dan purchase_line_id: append seperti kode 1
                def append_invoice(field, new_val):
                    existing = field or ""
                    exist_parts = [x.strip() for x in existing.split(",") if x.strip()]
                    new_parts = [x.strip() for x in new_val.split(",") if x.strip()]
                    filtered = [x for x in new_parts if x not in exist_parts]
                    if filtered:
                        return ", ".join(exist_parts + filtered)
                    return existing

                if (
                    move.sale_line_id
                    and move.product_id.product_tmpl_id == move.sale_line_id.product_id.product_tmpl_id
                ):
                    combined = append_invoice(move.sale_line_id.fal_customer_invoice_number, new_invoice)
                    move.sale_line_id.with_context(skip_sync=True).write({
                        "fal_customer_invoice_number": combined
                    })

                if (
                    move.purchase_line_id
                    and move.product_id.product_tmpl_id == move.purchase_line_id.product_id.product_tmpl_id
                ):
                    combined = append_invoice(move.purchase_line_id.fal_customer_invoice_number, new_invoice)
                    move.purchase_line_id.with_context(skip_sync=True).write({
                        "fal_customer_invoice_number": combined
                    })

                # 🔁 Rekursif propagasi
                origin_codes = list(set(re.split(r"\s*[-,]\s*", picking.origin or "")))
                origin_codes = [code.strip() for code in origin_codes if code.strip()]
                visited_invoice = set()
                for origin in origin_codes:
                    self._recursive_propagate_customer_invoice_number(
                        origin, new_invoice, visited_invoice, move.product_id.product_tmpl_id.id
                    )

        return res

    def _recursive_propagate_customer_invoice_number(
        self, code, invoice_number, visited=None, product_tmpl_id_target=None
    ):
        if visited is None:
            visited = set()
        if code in visited:
            return
        visited.add(code)

        def append_invoice(field_val, new_val):
            existing = field_val or ""
            exist_parts = [x.strip() for x in existing.split(",") if x.strip()]
            new_parts = [x.strip() for x in new_val.split(",") if x.strip()]
            filtered = [x for x in new_parts if x not in exist_parts]
            if filtered:
                return ", ".join(exist_parts + filtered)
            return existing

        # SALE ORDER
        sos = self.env["sale.order"].sudo().search([("name", "=", code)])
        for so in sos:
            for sol in so.order_line:
                if sol.product_id.product_tmpl_id.id == product_tmpl_id_target:
                    combined = append_invoice(sol.fal_customer_invoice_number, invoice_number)
                    sol.with_context(skip_sync=True).write({
                        "fal_customer_invoice_number": combined
                    })

            deliveries = self.env["stock.picking"].sudo().search([
                ("origin", "ilike", so.name)
            ])
            for delivery in deliveries:
                for move in delivery.move_ids_without_package:
                    if move.product_id.product_tmpl_id.id == product_tmpl_id_target:
                        if not move.fal_customer_invoice_number:
                            move.with_context(skip_sync=True).write({
                                "fal_customer_invoice_number": invoice_number
                            })

                deeper_origins = re.split(r"\s*[-,]\s*", delivery.origin or "")
                for deeper in deeper_origins:
                    if deeper:
                        self._recursive_propagate_customer_invoice_number(
                            deeper.strip(), invoice_number, visited, product_tmpl_id_target
                        )

            pos_from_so = self.env["purchase.order"].sudo().search([
                ("origin", "ilike", so.name)
            ])
            for po in pos_from_so:
                self._recursive_propagate_customer_invoice_number(
                    po.name, invoice_number, visited, product_tmpl_id_target
                )

        # PURCHASE ORDER
        pos = self.env["purchase.order"].sudo().search([("name", "=", code)])
        for po in pos:
            for pol in po.order_line:
                if pol.product_id.product_tmpl_id.id == product_tmpl_id_target:
                    combined = append_invoice(pol.fal_customer_invoice_number, invoice_number)
                    pol.with_context(skip_sync=True).write({
                        "fal_customer_invoice_number": combined
                    })

            receipts = self.env["stock.picking"].sudo().search([
                ("origin", "ilike", po.name)
            ])
            for receipt in receipts:
                for move in receipt.move_ids_without_package:
                    if move.product_id.product_tmpl_id.id == product_tmpl_id_target:
                        if not move.fal_customer_invoice_number:
                            move.with_context(skip_sync=True).write({
                                "fal_customer_invoice_number": invoice_number
                            })

                deeper_origins = re.split(r"\s*[-,]\s*", receipt.origin or "")
                for deeper in deeper_origins:
                    if deeper:
                        self._recursive_propagate_customer_invoice_number(
                            deeper.strip(), invoice_number, visited, product_tmpl_id_target
                        )

            if po.origin:
                origin_parts = re.split(r"\s*[-,]\s*", po.origin or "")
                for origin_code in origin_parts:
                    if origin_code:
                        self._recursive_propagate_customer_invoice_number(
                            origin_code.strip(), invoice_number, visited, product_tmpl_id_target
                        )

            sos_from_po = self.env["sale.order"].sudo().search([
                ("origin", "ilike", po.name)
            ])
            for so in sos_from_po:
                self._recursive_propagate_customer_invoice_number(
                    so.name, invoice_number, visited, product_tmpl_id_target
                )
