# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RecipeStep(models.Model):
    _name = "rm.recipe.step"
    _description = "A recipe step"
    _order = "sequence"

    def _get_default_sequence(self):
        return len(self.recipe_id.step_ids) + 1

    sequence = fields.Integer(default=_get_default_sequence)
    step_nb = fields.Char(compute="_compute_step_nb")
    recipe_id = fields.Many2one(comodel_name="rm.recipe", ondelete="cascade", required=True)
    description = fields.Text(required=True)
    time = fields.Integer(string="Time (min)")

    @api.depends('sequence')
    def _compute_step_nb(self):
        for rec in self:
            rec.step_nb = "#%s" % rec.sequence

    _sql_constraints = [
        (
            'check_time_not_negative',
            'CHECK(time >= 0)',
            "A step time cannot be negative.",
        ),
    ]
