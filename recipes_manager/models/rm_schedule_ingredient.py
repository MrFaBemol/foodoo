# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RmScheduleIngredient(models.Model):
    _name = "rm.schedule.ingredient"
    _description = "An ingredient with aggregated quantities"

    schedule_id = fields.Many2one(comodel_name="rm.schedule", ondelete='cascade')
    product_id = fields.Many2one(comodel_name="product.product", ondelete='cascade', readonly=True)
    product_category_id = fields.Many2one(related="product_id.categ_id")
    add_to_cart = fields.Boolean(related="product_id.add_to_cart")

    line_ids = fields.One2many(comodel_name="rm.schedule.ingredient.line", inverse_name="ingredient_id")
    line_count = fields.Integer(compute="_compute_ingredient_infos")
    total_qty = fields.Float(compute="_compute_ingredient_infos")
    uom_qty = fields.Many2one(comodel_name="uom.uom", compute="_compute_ingredient_infos")
    uom_count = fields.Integer(compute="_compute_ingredient_infos")
    uom_problem = fields.Boolean(compute="_compute_ingredient_infos")

    purchase_line_id = fields.Many2one(comodel_name="purchase.order.line")

    @api.depends('line_ids')
    def _compute_ingredient_infos(self):
        for ingredient in self:
            ingredient.line_count = len(ingredient.line_ids.recipe_id)
            ingredient.total_qty = sum(ingredient.line_ids.mapped('qty'))
            ingredient.uom_count = len(ingredient.line_ids.uom_qty)
            ingredient.uom_qty = False if ingredient.uom_count != 1 else ingredient.line_ids.uom_qty
            ingredient.uom_problem = ingredient.product_id.uom_id != ingredient.uom_qty


    def action_show_details(self):
        return {
            "name": _("Details for %s" % self.product_id.name),
            "type": 'ir.actions.act_window',
            "res_model": 'rm.schedule.ingredient.line',
            "views": [[False, "tree"]],
            "domain": [('id', 'in', self.line_ids.ids)],
            "target": 'new',
            "context": {
                **self.env.context,
            },
        }

