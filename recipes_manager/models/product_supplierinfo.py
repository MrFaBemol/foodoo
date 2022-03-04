# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    brand_id = fields.Many2one(comodel_name="product.brand")

