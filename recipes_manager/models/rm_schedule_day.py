# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RmScheduleDay(models.Model):
    _name = "rm.schedule.day"
    _description = "A schedule day"
    _inherit = ["meal.mixin"]


    schedule_id = fields.Many2one(comodel_name="rm.schedule", required=True, ondelete='cascade')
    sequence = fields.Integer()
    note = fields.Char()

    breakfast_recipe = fields.Many2one(comodel_name="rm.recipe", string="Breakfast")
    lunch_recipe = fields.Many2one(comodel_name="rm.recipe", string="Lunch")
    dinner_recipe = fields.Many2one(comodel_name="rm.recipe", string="Dinner")
    used_recipe_ids = fields.Many2many(comodel_name="rm.recipe", compute="_compute_used_recipe_ids")

    day_template_id = fields.Many2one(comodel_name="rm.schedule.template.day")

    @api.depends('breakfast_recipe', 'lunch_recipe', 'dinner_recipe')
    def _compute_used_recipe_ids(self):
        for day in self:
            day.used_recipe_ids = day.breakfast_recipe + day.lunch_recipe + day.dinner_recipe

