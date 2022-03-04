# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "A product brand"

    name = fields.Char(required=True)
