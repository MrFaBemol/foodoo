# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Recipe(models.Model):
    _name = "rm.recipe"
    _description = "A recipe with ingredients and steps"

    name = fields.Char(required=True)

    ingredient_ids = fields.One2many(comodel_name="rm.recipe.ingredient", inverse_name="recipe_id", string="Ingredients")
    tag_ids = fields.Many2many(comodel_name="rm.recipe.tag", string="Tags")
    step_ids = fields.One2many(comodel_name="rm.recipe.step", inverse_name="recipe_id", string="Steps")

    time_display = fields.Char(compute="_compute_time_display", string="Duration")

    user_rating = fields.Selection([
        ('0', 'No rating'),
        ('1', 'Meh'),
        ('2', 'Good'),
        ('3', 'Delicious')
    ],
        string='Rating', default='0', index=True)



    @api.depends('step_ids')
    def _compute_time_display(self):
        for rec in self:
            time_min = sum(rec.step_ids.mapped('time_min'))
            time_max = sum(rec.step_ids.mapped('time_max'))

            mod_min, mod_max = time_min % 5, time_max % 5
            time_min = time_min - mod_min if mod_min < 3 else time_min + (5-mod_min)
            time_max = time_max - mod_max if mod_max < 3 else time_max + (5-mod_max)

            rec.time_display = "%s min" % (time_min if time_min == time_max else ("%s-%s" % (time_min, time_max)))

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
