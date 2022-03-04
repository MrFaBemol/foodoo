# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"

    default_category = fields.Boolean(default=False)
    is_eatable = fields.Boolean()

    def check_default_category(self):
        default_category = self.search([('default_category', '=', True)])
        if len(default_category) > 1:
            raise UserError(_("You can only have one default category! Current: %s " % (default_category - self)[:1].display_name))

    @api.model
    def create(self, vals):
        res = super(ProductCategory, self).create(vals)
        self.check_default_category()
        return res

    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        self.check_default_category()
        return res


    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        self.is_eatable = self.parent_id.is_eatable


