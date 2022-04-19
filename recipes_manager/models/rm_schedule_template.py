# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RmScheduleTemplate(models.Model):
    _name = "rm.schedule.template"
    _description = "A schedule template"
    _inherit = ["meal.mixin"]

    name = fields.Char(required=True)

    breakfast_default_recipe = fields.Many2one(comodel_name="rm.recipe", string="Default breakfast")
    lunch_default_recipe = fields.Many2one(comodel_name="rm.recipe", string="Default lunch")
    dinner_default_recipe = fields.Many2one(comodel_name="rm.recipe", string="Default dinner")

    day_ids = fields.One2many(comodel_name="rm.schedule.template.day", inverse_name="template_id", required=True)

    day_qty = fields.Integer(compute="_compute_qty")
    meal_qty = fields.Integer(compute="_compute_qty")

    @api.depends('day_ids')
    def _compute_qty(self):
        for template in self:
            template.day_qty = len(template.day_ids)
            template.meal_qty = sum([template.day_qty - template.day_ids.mapped('%s_choice' % meal).count('none') for meal in ['breakfast', 'lunch', 'dinner']])


