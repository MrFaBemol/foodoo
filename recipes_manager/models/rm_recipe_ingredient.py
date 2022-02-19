# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RecipeIngredient(models.Model):
    _name = "rm.recipe.ingredient"
    _description = "An ingredient used in a recipe"

    product_id = fields.Many2one(comodel_name="product.product", required=True)
    product_uom = fields.Many2one(related="product_id.uom_id")
    product_uom_category = fields.Many2one(related="product_id.uom_id.category_id")

    qty = fields.Float(default=1.0)
    uom_qty = fields.Many2one(comodel_name="uom.uom", default=product_uom, domain="[('category_id', '=', product_uom_category)]")

    recipe_id = fields.Many2one(comodel_name="rm.recipe", required=True)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.uom_qty = self.product_uom
