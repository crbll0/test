# -*- coding: utf-8 -*-
from odoo import http
import logging

_logger = logging.getLogger(__name__)


class RealEstateWebsiteCrm(http.Controller):
    @http.route('/properties/', auth='public', website=True)
    def index(self, **kw):
        properties = http.request.env['real.estate.property'].search([])

        return http.request.render('real_estate_website_crm.index', {
            'properties': properties,
        })

    @http.route('/property/<model("real.estate.property"):property>', auth='public',
                website=True)
    def property(self, property=None, **kw):

        return http.request.render('real_estate_website_crm.property_page', {
            'property': property,
        })

    @http.route(
        '''/property/details/<model("real.estate.property", "[('website_id', 'in', (False, current_website_id))]"):property>''',
        type='http', auth="public", website=True)
    def jobs_apply(self, property, **kwargs):
        if not property.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        if 'real_estate_website_crm_error' in request.session:
            error = request.session.pop('real_estate_website_crm_error')
            default = request.session.pop('real_estate_website_crm_default')

        return request.render("real_estate_website_crm.property_contact", {
            'property': property,
            'error': error,
            'default': default,
        })