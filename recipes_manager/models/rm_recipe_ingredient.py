# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RecipeIngredient(models.Model):
    _name = "rm.recipe.ingredient"
    _description = "An ingredient used in a recipe"
    _order = "sequence"

    sequence = fields.Integer()
    product_ids = fields.Many2many(comodel_name="product.product", required=True, ondelete='cascade')
    product_uom_ids = fields.Many2many(comodel_name="uom.uom", compute="_compute_uom")
    product_uom_category_ids = fields.Many2many(comodel_name="uom.category", compute="_compute_uom")

    qty = fields.Float(default=1.0, required=True)
    uom_qty = fields.Many2one(comodel_name="uom.uom", required=True, domain="['|', ('name', 'in', ['g', 'kg']), ('category_id', 'in', product_uom_category_ids)]")
    note = fields.Char()

    recipe_id = fields.Many2one(comodel_name="rm.recipe", required=True)


    @api.depends('product_ids')
    def _compute_uom(self):
        for rec in self:
            rec.product_uom_ids = rec.product_ids.uom_id
            rec.product_uom_category_ids = rec.product_uom_ids.category_id

    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        if self.product_ids:
            if not self.uom_qty:
                self.uom_qty = self.product_uom_category_ids.uom_ids.filtered(lambda u: u.uom_type == 'reference')[:1]._origin
        else:
            self.uom_qty = False
            self.qty = 1.0
