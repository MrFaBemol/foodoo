# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Recipe(models.Model):
    _name = "rm.recipe"
    _description = "A recipe with ingredients and steps"

    name = fields.Char(required=True)

    ingredient_ids = fields.One2many(comodel_name="rm.recipe.ingredient", inverse_name="recipe_id", string="Ingredients")
    tag_ids = fields.Many2many(comodel_name="rm.recipe.tag", string="Tags")
    step_ids = fields.One2many(comodel_name="rm.recipe.step", inverse_name="recipe_id", string="Steps")


    def clean_step_numbers(self):
        for recipe in self:
            i = 1
            for step in recipe.step_ids.sorted('sequence'):
                if step.sequence != i:
                    step.write({'sequence': i})
                i += 1

    def write(self, vals):
        super(Recipe, self).write(vals)
        self.clean_step_numbers()
