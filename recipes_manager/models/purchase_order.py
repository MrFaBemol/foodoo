# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    schedule_id = fields.Many2one(comodel_name="rm.schedule")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    schedule_ingredient_id = fields.Many2one(comodel_name="rm.schedule.ingredient")

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        res.schedule_ingredient_id.write({'purchase_line_id': res.id})
        return res
