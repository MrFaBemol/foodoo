# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Recipe(models.Model):
    _name = "rm.recipe"
    _description = "A recipe with ingredients and steps"

    name = fields.Char(required=True)

    ingredient_ids = fields.One2many(comodel_name="rm.recipe.ingredient", inverse_name="recipe_id", string="Ingredients")
    tag_ids = fields.Many2many(comodel_name="rm.recipe.tag", string="Tags")
    step_ids = fields.One2many(comodel_name="rm.recipe.step", inverse_name="recipe_id", string="Steps")

    time_display = fields.Char(compute="_compute_time_display", string="Duration")
    time_min = fields.Integer(compute="_compute_time_display")
    time_max = fields.Integer(compute="_compute_time_display")

    meal_type = fields.Selection(
        selection=[
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner'),
        ]
    )

    serving_qty = fields.Integer(required=True, default=2, string="Servings")

    user_rating = fields.Selection([
            ('0', 'No rating'),
            ('1', 'Meh'),
            ('2', 'Good'),
            ('3', 'Delicious')
        ],
        string='Rating',
        default='0',
        index=True,
    )
    difficulty = fields.Selection([
        ('0', 'No rating'),
        ('1', 'Easy'),
        ('2', 'Medium'),
        ('3', 'Hard')
    ],
        string='Difficulty',
        default='0',
        index=True,
    )



    @api.depends('step_ids', 'tag_ids')
    def _compute_time_display(self):
        for recipe in self:
            ratio = 1.2 if self.env.ref('recipes_manager.recipe_tag_hellofresh') in recipe.tag_ids else 1
            time_min = int(sum(recipe.step_ids.mapped('time_min')) * ratio)
            time_max = int(sum(recipe.step_ids.mapped('time_max')) * ratio)

            mod_min, mod_max = time_min % 5, time_max % 5
            if mod_min < 3:
                time_min = time_min - mod_min
                time_max = time_max - mod_max
            else:
                time_min = time_min + (5-mod_min)
                time_max = time_max + (5-mod_max)

            recipe.time_display = "%s min" % (time_min if time_min == time_max else ("%s-%s" % (time_min, time_max)))
            recipe.time_min = time_min
            recipe.time_max = time_max

    def clean_step_numbers(self):
        for recipe in self:
            i = 1
            for step in recipe.step_ids.sorted('sequence'):
                if step.sequence != i:
                    step.write({'sequence': i})
                i += 1

    def add_automatic_tags(self):
        for recipe in self:
            tags = []

            # Times
            if recipe.time_max > 0:
                if recipe.time_max <= 15:
                    tags.append(self.env.ref('recipes_manager.recipe_tag_express').id)
                elif recipe.time_max <= 25:
                    tags.append(self.env.ref('recipes_manager.recipe_tag_rapido').id)

            # HelloFresh
            if recipe.step_ids.filtered_domain([('description', 'ilike', "HelloFresh")]):
                tags.append(self.env.ref('recipes_manager.recipe_tag_hellofresh').id)

            if tags:
                recipe.with_context(add_tags=True).write({'tag_ids': [(4, tag) for tag in tags]})

    def write(self, vals):
        super(Recipe, self).write(vals)
        self.clean_step_numbers()
        if not self.env.context.get('add_tags'):
            self.add_automatic_tags()

    @api.model
    def create(self, vals):
        res = super(Recipe, self).create(vals)
        res.add_automatic_tags()
        return res

    def copy(self, default=None):
        res = super(Recipe, self).copy(default)
        res.write({
            'ingredient_ids': [ingredient.copy().id for ingredient in self.ingredient_ids],
            'step_ids': [step.copy().id for step in self.step_ids],
        })
        return res
