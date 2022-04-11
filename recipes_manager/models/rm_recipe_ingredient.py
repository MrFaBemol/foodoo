# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RecipeIngredient(models.Model):
    _name = "rm.recipe.ingredient"
    _description = "An ingredient used in a recipe"
    _order = "sequence"

    sequence = fields.Integer()
    product_ids = fields.Many2many(comodel_name="product.product", required=True, ondelete='restrict', copy=True)
    product_add_to_cart = fields.Boolean(comodel_name="uom.category", compute="_compute_products_infos")
    product_uom_ids = fields.Many2many(comodel_name="uom.uom", compute="_compute_products_infos")
    product_uom_category_ids = fields.Many2many(comodel_name="uom.category", compute="_compute_products_infos")

    qty = fields.Float(default=1.0, required=True)
    uom_qty = fields.Many2one(comodel_name="uom.uom", required=True, copy=True)  # , domain="['|', ('name', 'in', ['g', 'kg']), ('category_id', 'in', product_uom_category_ids)]"
    note = fields.Char()

    recipe_id = fields.Many2one(comodel_name="rm.recipe", required=True, ondelete='cascade')


    @api.depends('product_ids')
    def _compute_products_infos(self):
        for rec in self:
            rec.product_add_to_cart = any(rec.product_ids.mapped('add_to_cart'))
            rec.product_uom_ids = rec.product_ids.uom_id
            rec.product_uom_category_ids = rec.product_uom_ids.category_id



    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        if self.product_ids:
            if not self.uom_qty:
                self.uom_qty = self.product_ids.uom_id[:1]  # self.product_uom_category_ids.uom_ids.filtered(lambda u: u.uom_type == 'reference')[:1]._origin
        elif len(self.product_ids) == 0:
            self.uom_qty = False
            self.qty = 1.0
