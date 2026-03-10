from odoo import _, fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    fal_customer_number = fields.Char(string="Customer Number")
