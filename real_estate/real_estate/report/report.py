#-*- coding:utf-8 -*-

import logging
from collections import defaultdict
from odoo import api, models

_logger = logging.getLogger(__name__)


class PaymentDetailsReport(models.AbstractModel):
    _name = 'report.real_estate.cumplimiento'
    _description = 'Real Estate Cumplimiento Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # report_obj = self.env['report']
        # report = report_obj._get_report_from_name('real_estate.report_cumplimiento')

        tipo = defaultdict(int)
        nacionalidad = defaultdict(int)
        residencia = defaultdict(int)
        categoria = defaultdict(int)
        actividad = defaultdict(int)

        temp_partner = self.env['res.partner'].browse(1)

        tipos = dict(temp_partner._fields['tipo_cliente'].selection)
        riesgos = dict(temp_partner._fields['calificacion_riesgo'].selection)
        actividades = dict(temp_partner._fields['actividad_economica'].selection)
        lst_partners = []

        cnt = len(docids)
        total = 0
        for o in self.env['account.payment'].browse(docids):
            total += o.amount

            partner_id = o.partner_id

            if partner_id.id not in lst_partners:
                nacionalidad[partner_id.nacionalidad_id.name] += 1
                residencia[partner_id.residencia_id.name] += 1
                categoria[riesgos.get(partner_id.calificacion_riesgo)] += 1
                actividad[actividades.get(partner_id.actividad_economica)] += 1

            partner_type = tipos.get(partner_id.tipo_cliente)
            if partner_type in tipo:
                if partner_id.id not in lst_partners:
                    tipo[partner_type]['cantidad'] += 1
                tipo[partner_type]['monto'] += o.amount
            else:
                tipo[partner_type] = {'cantidad': 1, 'monto': o.amount}
            lst_partners.append(partner_id.id)

        pagos = self.env['account.payment'].browse(docids)
        _logger.info(('VALOOR', self.env['res.partner']._fields['actividad_economica'].selection))

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'docs': self,
            'cantidad': cnt,
            'total': total,
            'pagos': pagos,
            'tipo': dict(tipo),
            'nacionalidad': dict(nacionalidad),
            'residencia': dict(residencia),
            'categoria': dict(categoria),
            'actividad': dict(actividad),
        }
        return docargs


class PaymentsReport(models.AbstractModel):
    _name = 'report.real_estate.cuadre_caja'
    _description = 'Real Estate Cuadre de Caja Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info(('DATA>>>>>>', data))
        cnt = len(docids)

        resume = {}
        pagos = self.env['account.payment'].browse(docids)

        for p in pagos:
            if p.currency_id.id in resume:
                resume[p.currency_id.id]['cnt'] += 1
                resume[p.currency_id.id]['total'] += p.amount

            else:
                resume[p.currency_id.id] = {
                    'currency': p.currency_id.name,
                    'cnt': 1,
                    'total': p.amount
                }

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'docs': self,
            'cantidad': cnt,
            'pagos': pagos,
            'resume': resume,
        }

        return docargs
