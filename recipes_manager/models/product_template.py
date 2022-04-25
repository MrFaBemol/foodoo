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

    recipe_ids = fields.Many2many(comodel_name="rm.recipe", compute="_compute_recipe_ids")
    recipe_count = fields.Integer(compute="_compute_recipe_ids")

    @api.depends('product_variant_ids', 'product_variant_id')
    def _compute_recipe_ids(self):
        for product in self:
            product.recipe_ids = product.product_variant_ids.ingredient_ids.recipe_id
            product.recipe_count = len(product.recipe_ids)


    def action_open_recipes(self):
        print("=====================================================")
        print(self.recipe_ids)
        print("=====================================================")

