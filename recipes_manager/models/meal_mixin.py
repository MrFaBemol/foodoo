# -*- coding: utf-8 -*-
from odoo import models


class MealMixin(models.AbstractModel):
    _name = "meal.mixin"
    _description = "A mixin used to get attributes"

    def meal(self, t, f):
        return getattr(self, "%s_%s" % (t, f))
