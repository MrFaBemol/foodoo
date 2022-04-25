# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    ingredient_ids = fields.Many2many(comodel_name="rm.recipe.ingredient")
    recipe_ids = fields.Many2many(comodel_name="rm.recipe", compute="_compute_recipe_ids")
    recipe_count = fields.Integer(compute="_compute_recipe_ids")

    @api.depends('ingredient_ids')
    def _compute_recipe_ids(self):
        for product in self:
            product.recipe_ids = product.ingredient_ids.recipe_id
            product.recipe_count = len(product.recipe_ids)



    def action_open_recipes(self):
        print("=====================================================")
        print(self.recipe_ids)
        print("=====================================================")

