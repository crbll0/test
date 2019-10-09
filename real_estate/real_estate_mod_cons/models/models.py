# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RealEstateModCons(models.Model):
    _name = 'real.estate.mod.cons'
    _description = 'Real Estate Mod Cons'

    name = fields.Char()


class RealEstateProperty(models.Model):
    _inherit = 'real.estate.property'

    mod_cons_ids = fields.Many2many('real.estate.mod.cons', string='Comodidades')

class RealEstateProjectModCons(models.Model):
    _name = 'real.estate.project.mod.cons'
    _description = 'Real Estate Project Mod Cons'

    name = fields.Char()


class RealEstateProject(models.Model):
    _inherit = 'real.estate.project'

    mod_cons_ids = fields.Many2many('real.estate.project.mod.cons', string='Comodidades')
