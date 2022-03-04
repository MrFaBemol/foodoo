# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RmScheduleDay(models.Model):
    _name = "rm.schedule.day"
    _description = "A schedule day"


    schedule_id = fields.Many2one(comodel_name="rm.schedule")
    sequence = fields.Integer()
    note = fields.Char()

    breakfast_recipe = fields.Many2one(comodel_name="rm.recipe", string="Breakfast")
    lunch_recipe = fields.Many2one(comodel_name="rm.recipe", string="Lunch")
    dinner_recipe = fields.Many2one(comodel_name="rm.recipe", string="Dinner")

    day_template_id = fields.Many2one(comodel_name="rm.schedule.template.day")

