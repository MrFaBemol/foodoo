# -*- coding: utf-8 -*-
from random import randint, randrange
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Recipe(models.Model):
    _name = "rm.recipe"
    _description = "A recipe with ingredients and steps"

    def name_get(self):
        limit = 50
        return [(s.id, s.name if len(s.name) < limit else s.name[:limit-3] + " [...]") for s in self]

    name = fields.Char(required=True)

    ingredient_ids = fields.One2many(comodel_name="rm.recipe.ingredient", inverse_name="recipe_id", string="Ingredients")
    tag_ids = fields.Many2many(comodel_name="rm.recipe.tag", string="Tags")
    step_ids = fields.One2many(comodel_name="rm.recipe.step", inverse_name="recipe_id", string="Steps")

    time_display = fields.Char(compute="_compute_time_display", string="Duration")
    time_min = fields.Integer(compute="_compute_time_display")
    time_max = fields.Integer(compute="_compute_time_display")

    used_schedule_ids = fields.Many2many(comodel_name="rm.schedule", compute="_compute_used_schedule_ids", compute_sudo=True)
    last_used = fields.Date(compute="_compute_used_schedule_ids", store=True)
    weight_rating = fields.Integer(compute="_compute_weight_rating")


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

    def _compute_used_schedule_ids(self):
        for recipe in self:
            recipe.used_schedule_ids = self.env['rm.schedule.day'].search([
                ('schedule_id.state', 'in', ['validated', 'done']),
                '|', '|',
                    ('breakfast_recipe', '=', recipe.id),
                    ('lunch_recipe', '=', recipe.id),
                    ('dinner_recipe', '=', recipe.id)
            ]).schedule_id
            recipe.last_used = recipe.used_schedule_ids.sorted(key='date_to', reverse=True)[:1].date_to

    @api.depends('last_used', 'user_rating', 'difficulty')
    def _compute_weight_rating(self):
        # Todo: add a tag weight
        for recipe in self:
            weight_rating = 5
            weight_rating += 2 * int(recipe.user_rating)
            weight_rating -= 1 * int(recipe.difficulty)
            weight_rating += (fields.Date.today() - recipe.last_used).days // 7 if recipe.last_used else 15
            recipe.weight_rating = max(weight_rating, 1)


    def generate_ingredients_list(self, serving_qty):
        """
            Generate ingredients qty for passed servings quantity
            Also pick one ingredient if there are several
        :return: list[] of dict{}
        """
        self.ensure_one()
        ingredients_list = []
        for ingredient in self.ingredient_ids:
            i = randrange(len(ingredient.product_ids))
            product = ingredient.product_ids[i:i+1]
            ingredients_list.append({
                'product_id': product,
                'qty': round(ingredient.qty * (serving_qty / self.serving_qty), 2),
                'uom_qty': ingredient.uom_qty,
                'note': ingredient.note,
            })
        return ingredients_list


    def pick_one(self):
        """
        Pick a recipe among self based on priority (weight_rating)
        :return: rm.recipe() record
        """
        if not self:
            raise UserError(_("You can't pick one recipe of there is none !"))
        self._compute_weight_rating()
        pick = randint(1, sum(self.mapped('weight_rating')))
        step = 0
        for recipe in self.sorted(lambda r: (r.weight_rating, r.id)):
            if pick <= recipe.weight_rating + step:
                return recipe
            step += recipe.weight_rating


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
