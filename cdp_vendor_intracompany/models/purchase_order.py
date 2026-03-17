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

	    #issue ticket 13766, reserve function not working
        so_moves = so.picking_ids.mapped('move_ids_without_package')
        po_moves = self.picking_ids.mapped('move_ids_without_package')
        for so_move in so_moves:
            matched_po_moves = po_moves.filtered(lambda m: m.product_id == so_move.product_id)
            if matched_po_moves:
                so_move.write({'move_orig_ids':[(6,0,matched_po_moves.ids)]})

    def button_confirm(self):
        res = super().button_confirm()
        for po in self:
            po._cdp_update_move_dest_ids(po.fal_all_recorded_sale)
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _create_or_update_picking(self):
        return True
    
    # @api.model_create_multi
    # def create(self, vals_list):        
    #     res = super().create(vals_list)
    #     self.env['ir.logging'].sudo().create({
    #             'name': 'create',
    #             'type': 'server',
    #             'level': 'INFO',
    #             'dbname': self.env.cr.dbname,
    #             'message': str(vals_list),
    #             'func': "create",
    #             'path': '',
    #             'line': '1',
    #         })
    #     return res

    # def write(self, values):
    #     res = super().write(values)
    #     message = ""
    #     if 'move_dest_ids' in values and values['move_dest_ids']:
    #         for command in values['move_dest_ids']:
                
    #             if command[0] == 4:
    #                 move_id = command[1]
    #                 message += "test"
    #                 move = self.env['stock.move'].browse(move_id)
    #                 if move.exists():
    #                     message += str(move)
    #                     values['product_qty'] = move.product_uom_qty
    #     self.env['ir.logging'].sudo().create({
    #             'name': 'write',
    #             'type': 'server',
    #             'level': 'INFO',
    #             'dbname': self.env.cr.dbname,
    #             'message': str(values) + message,
    #             'func': "write",
    #             'path': '',
    #             'line': '1',
    #         })
    #     # raise EnvironmentError
    #     return res
    
    

