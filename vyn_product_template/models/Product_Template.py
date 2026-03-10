from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    vyn_marque = fields.Char(string="Brand", store=True)
    vyn_ancien_code = fields.Char(string="Old code", store=True, translate=True)
    vyn_uc_per_unit = fields.Float(string="uc per unit", store=True)
    vyn_unit_per_inner = fields.Float(string="unit per inner", store=True)
    vyn_packing_type = fields.Char(string="Packing type", store=True, translate=True)
