# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RmScheduleIngredientLine(models.Model):
    _name = "rm.schedule.ingredient.line"
    _description = "A detailed ingredient line"

    ingredient_id = fields.Many2one(comodel_name="rm.schedule.ingredient", ondelete="cascade")
    recipe_id = fields.Many2one(comodel_name="rm.recipe")
    qty = fields.Float()
    uom_qty = fields.Many2one(comodel_name="uom.uom")
    note = fields.Char()

