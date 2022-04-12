# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)



MEAL_TYPES = ['breakfast', 'lunch', 'dinner']

class RmSchedule(models.Model):
    _name = "rm.schedule"
    _description = "A schedule for recipes"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    has_correct_date_range = fields.Boolean(compute="_compute_has_correct_date_range")
    used_recipe_ids = fields.Many2many(comodel_name="rm.recipe", compute="_compute_used_recipe_ids")

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('generated', 'Generated'),
            ('validated', 'Validated'),
            ('done', 'Done'),
        ],
        required=True,
        default='draft',
    )

    template_id = fields.Many2one(comodel_name="rm.schedule.template")
    template_day_ids = fields.One2many(comodel_name="rm.schedule.template.day", inverse_name="schedule_id")
    day_ids = fields.One2many(comodel_name="rm.schedule.day", inverse_name="schedule_id")

    min_serving_per_recipe = fields.Integer(required=True, default=2, string="Min. servings")


    @api.depends('day_ids')
    def _compute_used_recipe_ids(self):
        for schedule in self:
            schedule.used_recipe_ids = schedule.day_ids.used_recipe_ids

    @api.depends('template_id', 'date_to', 'date_from')
    def _compute_has_correct_date_range(self):
        for schedule in self:
            schedule.has_correct_date_range = not schedule.template_id or (schedule.date_to - schedule.date_from).days + 1 == schedule.template_id.day_qty

    def name_get(self):
        return [(s.id, "%s → %s (%s)" % (s.date_from.strftime("%d %B"), s.date_to.strftime("%d %B"), s.date_to.year)) for s in self]


    @api.onchange('template_id')
    def _onchange_template_id(self):
        # Todo: Add a confirmation dialog
        if self.template_id:
            self.template_day_ids = [day.copy(default={'template_id': False}).id for day in self.template_id.day_ids]


    def get_meal_qty_needed(self):
        self.ensure_one()
        meal_sequence = []
        meal_qty_needed = defaultdict(int)
        for day in self.day_ids:
            for meal in MEAL_TYPES:
                if getattr(day.day_template_id, '%s_choice' % meal) == 'random':
                    meal_qty_needed[meal] += 1
                    meal_sequence.append(meal)
        return meal_sequence, meal_qty_needed


    def cut_meal_sequence(self, sequence, longest_step=0, offset=0):
        if not longest_step:
            longest_step = self.min_serving_per_recipe
        res = []
        res_weight = 0
        meal_qty = 0

        while sequence:
            step = longest_step if offset == meal_qty else self.min_serving_per_recipe
            meal_qty += step

            sub = sequence[:step]
            sequence = sequence[step:]

            res.append(sub)
            res_weight += len(set(sub))

        return res, res_weight

    def get_best_meal_sequence(self, sequence):
        self.ensure_one()
        sequence_length = len(sequence)

        remainder = sequence_length % self.min_serving_per_recipe
        if remainder:
            longest_step = self.min_serving_per_recipe + remainder
            offset = 0
            best_sequence = []
            best_weight = 100

            # Do all the possibilities:
            while offset + longest_step < sequence_length:
                res, res_weight = self.cut_meal_sequence(sequence, longest_step, offset)
                if res_weight < best_weight:
                    best_sequence = res
                    best_weight = res_weight
                offset += self.min_serving_per_recipe

            return best_sequence, best_weight
        else:
            return self.cut_meal_sequence(sequence)


    def clean_days(self):
        for schedule in self:
            schedule.day_ids.exists().unlink()

    def generate_days(self):
        for schedule in self:
            schedule.clean_days()
            vals_list = []
            template = schedule.template_id
            for day in schedule.template_day_ids:
                vals = {
                    'schedule_id': schedule.id,
                    'sequence': day.sequence,
                    'note': day.note,
                    'day_template_id': day.id,
                }
                # Fill with the default values of the template
                if template:
                    for meal in MEAL_TYPES:
                        vals['%s_recipe' % meal] = getattr(template, "%s_default_recipe" % meal).id if getattr(day, "%s_choice" % meal) == 'default' else False
                vals_list.append(vals)
            schedule.day_ids = self.env['rm.schedule.day'].create(vals_list)

    def generate_schedule(self):
        recipes = {meal: self.env['rm.recipe'].search(['|', ('meal_type', '=', False), ('meal_type', '=', meal)]) for meal in MEAL_TYPES}

        for schedule in self:
            meal_sequence, meal_qty_needed = schedule.get_meal_qty_needed()
            optimal_meal_sequences, weight = self.get_best_meal_sequence(meal_sequence)

            selected_recipes = self.env['rm.recipe']
            schedule_recipes_sequence = []

            for sub_sequence in optimal_meal_sequences:
                possible_recipes = recipes[sub_sequence[0]]
                for meal in sub_sequence[1:]:
                    possible_recipes &= recipes[meal]
                possible_recipes -= selected_recipes

                recipe = possible_recipes.pick_one()

                schedule_recipes_sequence.extend([recipe for i in sub_sequence])
                selected_recipes |= recipe

            for day in self.day_ids:
                for meal in MEAL_TYPES:
                    if getattr(day.day_template_id, "%s_choice" % meal) == 'random':
                        recipe = schedule_recipes_sequence.pop(0)
                        day.write({'%s_recipe' % meal: recipe.id})






    def unlink(self):
        used_recipe_ids = self.used_recipe_ids
        super(RmSchedule, self).unlink()
        used_recipe_ids._compute_used_schedule_ids()




    def action_confirm(self):
        self.ensure_one()
        self.state = 'pending'
        self.generate_days()

    def action_generate_schedule(self):
        """
        Generate recipes for each day.
        If the schedule has already been generated, clean & regenerate the days before.
        """
        self.ensure_one()
        if self.state == 'generated':
            self.generate_days()
        else:
            self.state = 'generated'
            pass

        try_amount = 1
        while try_amount <= 3:
            try:
                self.generate_schedule()
                break
            except Exception as e:
                _logger.warning("Fail to generated schedule (try #%s): %s " % (try_amount, e))
                try_amount += 1

    def action_validate(self):
        self.ensure_one()
        self.state = 'validated'
        self.used_recipe_ids._compute_used_schedule_ids()

