# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    forma_pago = fields.Char(string='Forma de Pago')
    real_estate_contract_id = fields.Many2one('real.estate.contract')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_id = fields.Many2one('real.estate.property', 'Propiedad/Apartamento')

    @api.multi
    def create_property_contract(self):
        if not self.partner_id:
            raise UserError('Debes de Asignarle el Cliente a la Oportunidad.')

        actions = {
            "type": "ir.actions.act_window",
            "res_model": "real.estate.contract",
            "views": [ [False, "form"]],
            "context": {
                'default_partner_id': self.partner_id.id,
                'default_property_id': self.property_id.id,
                'default_property_amount': self.property_id.amount,
                'default_separacion': self.property_id.separacion,
                'default_lead_id': self.id,
                'default_vendedor_id': self.user_id.id,

            },
        }

        return actions


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    estado_civil = fields.Selection([
            ('soltero', 'Soltero(a)'),
            ('casado', 'Casado(a)'),
        ], string='Estado Civil')
    
    actividad_economica = fields.Selection([
        ('ama_de_casa', 'Ama de Casa'),
        ('privado', 'Empleado Privado'),
        ('publico', 'Empleado Publico'),
        ('ensenanzas', 'Ensenanzas'),
        ('estudiante', 'Estudiante'),
        ('pensionado', 'Juvilado/Pensionado'),
        ('pindependiente', 'Profesional Independiente'),
        ('tindependiente', 'Trabajador Independiente'),
        ('otros', 'Otros'),
    ], string='Actividad Economica')

    tipo_cliente = fields.Selection([
        ('fisica', 'Persona Fisica'),
        ('juridica', 'Persona Juridica'),
        ('peps', 'PEPS'),
    ], string='Tipo de Cliente')

    calificacion_riesgo = fields.Selection([
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto')
    ], string='Calificacion de Riesgo', default='bajo')

    nacionalidad_id = fields.Many2one('res.country', string='Nacional de')

    residencia_id = fields.Many2one('res.country', string='Reside en')
