from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # Overide Cluedoo: Defailt False
    consolidated_billing = fields.Boolean(
        string="Consolidated Billing",
        default=False,
        help="Create one invoice for all orders related to same customer and same invoicing address",
    )

    # @api.onchange("consolidated_billing")
    # def _onchange_consolidated_billing(self):
    #     if self.consolidated_billing:
    #         sale_orders = self._context.get("active_ids")
    #         if sale_orders:
    #             orders = self.env["sale.order"].browse(sale_orders)
    #             customer_numbers = orders.mapped("fal_customer_number")
    #             if len(set(customer_numbers)) > 1:
    #                 raise ValidationError(
    #                     _(
    #                         "You cannot enable Consolidated Billing for Sale Orders with different Customer Numbers."
    #                     )
    #                 )

    def _create_invoices(self, sale_orders):
        # Run the invoice process as usual
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)

        if self.consolidated_billing:
            # If consolidated, all invoices must have the same fal_customer_number
            customer_numbers = sale_orders.mapped("fal_customer_number")
            if customer_numbers:
                res.write(
                    {
                        "fal_customer_number": customer_numbers[0],
                    }
                )
        else:
            for invoice in res:
                related_so = sale_orders.filtered(
                    lambda so: invoice.invoice_origin
                    and so.name in invoice.invoice_origin
                )
                if related_so:
                    invoice.fal_customer_number = related_so[0].fal_customer_number

        return res




class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    
    def process(self):
        res = super(StockBackorderConfirmation, self).process()

        # Cari semua picking yang baru terbentuk dari backorder
        backordered_pickings = self.env['stock.picking'].search([
            ('backorder_id', 'in', self.pick_ids.ids)
        ])

        for picking in backordered_pickings:
            for move in picking.move_ids_without_package:
                # Kosongkan hanya jika move ini baru (hasil backorder)
                move.with_context(skip_sync=True).write({
                    'fal_customer_invoice_number': False
                })

        return res