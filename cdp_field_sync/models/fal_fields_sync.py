from odoo import models, fields

import logging
_logger = logging.getLogger(__name__)

class FalFieldSync(models.Model):
    _name = "cdp.fields.sync"
    _description = "Field Sync Configuration"

    cdp_from_model_id = fields.Many2one("ir.model", string="From Model", required=True, ondelete='cascade')
    cdp_from_field_id = fields.Many2one(
        "ir.model.fields",
        string="From Field",
        domain="[('model_id', '=', cdp_from_model_id)]",
    )

    cdp_to_model_id = fields.Many2one("ir.model", string="To Model", required=True, ondelete='cascade')
    cdp_to_field_id = fields.Many2one(
        "ir.model.fields",
        string="To Field",
        domain="[('model_id', '=', cdp_to_model_id)]",
    )


    def fal_run_sync_record(self, from_model_name, to_model_name, from_record, to_record):
        syncs = self.search([
            ('cdp_from_model_id.model', '=', from_model_name),
            ('cdp_to_model_id.model', '=', to_model_name),
        ])
        for sync in syncs:
            from_field = sync.cdp_from_field_id.name
            to_field = sync.cdp_to_field_id.name
            for source_rec in from_record:
                value = source_rec[from_field]
                for target_rec in to_record:
                    # _logger.info(
                    #     f"[SYNC DEBUG] {from_model_name} → {to_model_name} | "
                    #     f"{from_field} → {to_field} | Value: {value} | "
                    #     f"Target Record: {target_rec.display_name}")
                    target_rec.write({to_field: value})

