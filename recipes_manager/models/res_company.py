# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    active = fields.Boolean(default=True)
