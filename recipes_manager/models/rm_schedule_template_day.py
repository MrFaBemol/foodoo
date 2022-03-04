# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RmScheduleTemplateDay(models.Model):
    _name = "rm.schedule.template.day"
    _description = "A template day"

    template_id = fields.Many2one(comodel_name="rm.schedule.template")
    schedule_id = fields.Many2one(comodel_name="rm.schedule")
    sequence = fields.Integer(default=10)
    note = fields.Char()

    def _get_selection_choices(self):
        return [
            ('random', 'Random'),
            ('default', 'Default'),
            ('none', '-'),
        ]

    breakfast_choice = fields.Selection(
        selection=_get_selection_choices,
        required=True,
        default='default',
        string="Breakfast",
    )
    lunch_choice = fields.Selection(
        selection=_get_selection_choices,
        required=True,
        default='random',
        string="Lunch",
    )
    dinner_choice = fields.Selection(
        selection=_get_selection_choices,
        required=True,
        default='random',
        string="Dinner",
    )

    def write(self, vals):
        super(RmScheduleTemplateDay, self).write(vals)
        self.filtered(lambda d: not d.template_id and not d.schedule_id).unlink()

