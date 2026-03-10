from odoo import models, api, fields, _
import re


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fal_customer_number = fields.Char(string="Customer Number")

    @api.model
    def _recursive_propagate_customer_number(self, code, customer_number, visited=None):
        if visited is None:
            visited = set()
        if code in visited:
            return
        visited.add(code)

        pattern = r"\b{}\b".format(re.escape(code))

        # 1. Check Sale Order
        sos = self.env["sale.order"].sudo().search([("name", "=", code)])
        for so in sos:
            if re.search(pattern, so.name, re.IGNORECASE):
                so.with_context(skip_sync=True).write(
                    {"fal_customer_number": customer_number}
                )

                # 1a. Propagation to Delivery Order
                deliveries = (
                    self.env["stock.picking"]
                    .sudo()
                    .search(
                        [
                            ("origin", "ilike", so.name),
                        ]
                    )
                )
                for delivery in deliveries:
                    if delivery.origin and re.search(
                        pattern, delivery.origin, re.IGNORECASE
                    ):
                        delivery.with_context(skip_sync=True).write(
                            {"fal_customer_number": customer_number}
                        )
                        deeper_origins = re.split(
                            r"\s*[-,]\s*", delivery.origin.strip()
                        )
                        for deeper in deeper_origins:
                            if deeper:
                                self._recursive_propagate_customer_number(
                                    deeper.strip(), customer_number, visited
                                )

                # 1b. If SO from PO (dropship)
                pos_from_so = (
                    self.env["purchase.order"]
                    .sudo()
                    .search([("origin", "ilike", so.name)])
                )
                for po in pos_from_so:
                    if re.search(
                        r"\b{}\b".format(re.escape(so.name)),
                        po.origin or "",
                        re.IGNORECASE,
                    ):
                        self._recursive_propagate_customer_number(
                            po.name, customer_number, visited
                        )

        # 2. Check Purchase Order directly without loading all companies
        pos = self.env["purchase.order"].sudo().search([("name", "=", code)])
        for po in pos:
            if re.search(pattern, po.name, re.IGNORECASE):
                po.with_context(skip_sync=True).write(
                    {"fal_customer_number": customer_number}
                )

                # 2a. Propagation to Receipt
                receipts = (
                    self.env["stock.picking"]
                    .sudo()
                    .search(
                        [
                            ("origin", "ilike", po.name),
                        ]
                    )
                )
                for receipt in receipts:
                    if receipt.origin and re.search(
                        pattern, receipt.origin, re.IGNORECASE
                    ):
                        receipt.with_context(skip_sync=True).write(
                            {"fal_customer_number": customer_number}
                        )
                        deeper_origins = re.split(r"\s*[-,]\s*", receipt.origin.strip())
                        for deeper in deeper_origins:
                            if deeper:
                                self._recursive_propagate_customer_number(
                                    deeper.strip(), customer_number, visited
                                )

                # 2b. If the PO has an origin
                if po.origin:
                    deeper_origins = re.split(r"\s*[-,]\s*", po.origin.strip())
                    for deeper in deeper_origins:
                        if deeper:
                            self._recursive_propagate_customer_number(
                                deeper.strip(), customer_number, visited
                            )

                # 2c. Additional: PO generate SO (dropship)
                sos_from_po = (
                    self.env["sale.order"].sudo().search([("origin", "ilike", po.name)])
                )
                for so in sos_from_po:
                    if re.search(
                        r"\b{}\b".format(re.escape(po.name)),
                        so.origin or "",
                        re.IGNORECASE,
                    ):
                        self._recursive_propagate_customer_number(
                            so.name, customer_number, visited
                        )

    def write(self, vals):
        if self.env.context.get("skip_sync"):
            return super().write(vals)

        res = super().write(vals)

        for picking in self:
            fal_changed = "fal_customer_number" in vals
            origin_changed = "origin" in vals

            if (
                (fal_changed or origin_changed)
                and picking.fal_customer_number
                and picking.origin
            ):
                origin_parts = re.split(r"\s*[-,]\s*", picking.origin.strip())
                origin_parts = [part.strip() for part in origin_parts if part.strip()]
                for origin_code in origin_parts:
                    self._recursive_propagate_customer_number(
                        origin_code, picking.fal_customer_number
                    )

        return res

   