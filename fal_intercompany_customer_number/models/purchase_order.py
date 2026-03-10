from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    fal_customer_number = fields.Char(string="Customer Number", copy=False)

    def action_create_invoice(self):
        # Get the names of all companies involved in the PO
        company_names = set(self.mapped("company_id.name"))

        # If all PO are only from company "WEITAI", skip validation.
        # if not (len(company_names) == 1 and "WEITAI" in company_names):
        #     # Validation fal_customer_number must be the same
        #     customer_numbers = set(filter(None, self.mapped("fal_customer_number")))
        #     if len(customer_numbers) > 1:
        #         raise ValidationError(
        #             _(
        #                 "You cannot create invoices from purchase orders with different Customer Numbers.\n"
        #                 "Selected Customer Numbers: %s"
        #             )
        #             % ", ".join(sorted(customer_numbers))
        #         )

        # Continue the process if validation passes or is skipped
        res = super(PurchaseOrder, self).action_create_invoice()

        # Set fal_customer_number on invoice if any
        combined_customer_number = next(
            iter(set(filter(None, self.mapped("fal_customer_number")))), False
        )

        all_invoices = self.mapped("invoice_ids")
        if all_invoices and combined_customer_number:
            all_invoices.write({"fal_customer_number": combined_customer_number})

        return res
