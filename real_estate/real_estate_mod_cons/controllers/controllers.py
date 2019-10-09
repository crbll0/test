# -*- coding: utf-8 -*-
from odoo import http

# class RealEstateModCons(http.Controller):
#     @http.route('/real_estate_mod_cons/real_estate_mod_cons/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real_estate_mod_cons/real_estate_mod_cons/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('real_estate_mod_cons.listing', {
#             'root': '/real_estate_mod_cons/real_estate_mod_cons',
#             'objects': http.request.env['real_estate_mod_cons.real_estate_mod_cons'].search([]),
#         })

#     @http.route('/real_estate_mod_cons/real_estate_mod_cons/objects/<model("real_estate_mod_cons.real_estate_mod_cons"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real_estate_mod_cons.object', {
#             'object': obj
#         })