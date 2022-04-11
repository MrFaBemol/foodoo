# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RecipeStep(models.Model):
    _name = "rm.recipe.step"
    _description = "A recipe step"
    _order = "sequence"

    def _get_default_sequence(self):
        return len(self.recipe_id.step_ids) + 1

    sequence = fields.Integer(default=_get_default_sequence, copy=True)
    step_nb = fields.Char(compute="_compute_step_nb")
    recipe_id = fields.Many2one(comodel_name="rm.recipe", ondelete="cascade", required=True)
    description = fields.Text(required=True)
    time = fields.Char(string="Time (min)")
    time_min = fields.Integer(compute="_compute_step_times")
    time_max = fields.Integer(compute="_compute_step_times")

    @api.depends('sequence')
    def _compute_step_nb(self):
        for rec in self:
            rec.step_nb = "#%s" % rec.sequence

    @api.depends('time')
    def _compute_step_times(self):
        for rec in self:
            if rec.time:
                times = rec.time.split("-")
                rec.time_min = int(times[0])
                rec.time_max = int(times[1]) if len(times) > 1 else int(times[0])
                if rec.time_min > rec.time_max:
                    raise UserError(_("The min time is higher than the max time! (%s > %s)" % (rec.time_min, rec.time_max)))
            else:
                rec.time_min = 0
                rec.time_max = 0

    _sql_constraints = [
        (
            'check_time_not_negative',
            'CHECK(time >= 0)',
            "A step time cannot be negative.",
        ),
    ]
