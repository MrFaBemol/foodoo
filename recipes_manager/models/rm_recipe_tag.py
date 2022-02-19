# -*- coding: utf-8 -*-
from random import randint
from odoo import api, fields, models, _


class RecipeTag(models.Model):
    _name = "rm.recipe.tag"
    _description = "A tag to be used in recipe"

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(default=_get_default_color)
    name = fields.Char(required=True)

