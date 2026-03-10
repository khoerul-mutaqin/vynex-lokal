from odoo import models, fields


class VynResPartner(models.Model):
    _inherit = "res.partner"
    vyn_partner_code = fields.Char(string="Partner", store=True)
