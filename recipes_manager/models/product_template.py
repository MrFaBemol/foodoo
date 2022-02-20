# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_ok = fields.Boolean(default=False)
    categ_id = fields.Many2one(comodel_name="product.category", default=lambda self: self.env['product.category'].search([('default_category', '=', True)])[:1])

    is_eatable = fields.Boolean(related="categ_id.is_eatable")
    add_to_cart = fields.Boolean(default=True, help="""
        If true, this product will be added in the list of ingredients to order\n
        Otherwise, it will be displayed in the standard list to check (e.g. Salt, Pepper, Oil, ...)
    """)


