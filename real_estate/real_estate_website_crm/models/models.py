# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _inherit = ['real.estate.property', 'website.published.mixin']

    website_description = fields.Text('Website Description')

    def _compute_website_url(self):
        for property in self:
            property.website_url = "/property/%s" % (property.id)
