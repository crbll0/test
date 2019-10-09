# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from num2words import num2words

_logger = logging.getLogger(__name__)


class PaymentQuota(models.Model):
    _name = 'payment.quota'

    name = fields.Char(string='Pago' , readonly=1)
    partner_id = fields.Many2one('res.partner', string='Cliente')
    contract_id = fields.Many2one('real.estate.contract')
    property_id = fields.Many2one(related='contract_id.property_id')
    payment_id = fields.Many2one('account.payment', string='Pago asociado')

    currency_id = fields.Many2one(related='contract_id.property_currency_id')
    date = fields.Date(default=fields.Date.today())
    amount = fields.Float(string='Monto a pagar', compute='get_amount')
    monto_letra = fields.Char(readonly='1')
    journal_id = fields.Many2one('account.journal', string='Diario/Caja')

    forma_pago = fields.Selection([
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Cheque', 'Cheque'),
        ('Transferencia', 'Transferencia'),
    ], string='Forma de Pago')
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('cancel', 'Cancelado'),
        ('done', 'Hecho'),
    ], string='Estado', default='draft')

    quota_ids = fields.One2many('payment.quota.line', 'pago_id')

    tasa = fields.Float(string='Tasa', default=1)
    monto_divisa = fields.Float(string='Monto')
    currency_payment_id = fields.Many2one('res.currency', string='Divisa del Pago',
                                          default=lambda self: self.currency_id.id)

    @api.depends('monto_divisa', 'tasa', 'currency_id', 'currency_payment_id')
    def get_amount(self):
        for r in self:
            moneda_cuota = r.currency_id.name
            moneda_pago = r.currency_payment_id.name

            if moneda_cuota == moneda_pago:
                r.amount = r.monto_divisa
                
            else:
                if moneda_pago == "DOP":
                    r.amount = r.monto_divisa / r.tasa

                else:
                    r.amount = r.monto_divisa * r.tasa

    def amount_word(self, monto):
        amt = str('{0:.2f}'.format(monto))
        amt_lst = amt.split('.')
        amt_word = num2words(int(amt_lst[0]),lang='es')
        lst = amt_word.split(' ')
        lst.append(' con '+amt_lst[1]+'/'+str(100))
        value = ' '.join(lst)
        value = value.upper()
        return value

    def _get_quota_info(self):
        contract = self.contract_id

        amount = self.amount

        l = []
        for quota_id in contract.quota_ids:
            if quota_id.amount_paid == quota_id.amount or quota_id.residual == 0:
                continue

            if amount >= quota_id.residual:
                monto = quota_id.amount - quota_id.amount_paid
                amount -= monto
                note = 'Pago de %s' % quota_id.name

            else:
                monto = amount
                amount -= monto
                note = 'Avance de %s' % quota_id.name

            l.append(
                {
                    'quota_id': quota_id.id,
                    # 'currency_id': quota_id.currency_id.id,
                    'amount': quota_id.amount,
                    'to_pay': monto,
                    'pago_id': self,
                    'amount_paid': quota_id.amount_paid,
                    'residual': quota_id.amount - quota_id.amount_paid,
                    'note': note,
                }
            )

            if amount <= 0:
                break

        return l

    @api.onchange('amount')
    def _onchange_amount(self):
       
        monto_letra = self.amount_word(self.amount)
        self.quota_ids = [(5, 0, 0)]
        
        l = [(0, 0, i) for i in self._get_quota_info()]
        # self.quota_ids = l
        return {'value': {'quota_ids': l, 'monto_letra': monto_letra}}
    
    @api.multi
    def action_done(self):
        if not self.payment_id:
            payment = self.generate_payment()
            self.write({'state':'done', 'payment_id': payment.id})
        else:
            self.payment_id.post()
            self.state = 'done'
    
    @api.multi
    def action_cancel(self):
        self.payment_id.cancel()
        self.state = 'cancel'
    
    
    @api.multi
    def action_to_draft(self):
        self.payment_id.action_draft()
        self.state = 'draft'
    
    @api.multi
    def generate_payment(self):
        contract = self.contract_id
        quota = self.env['real.estate.contract.quota']

        #note = ''
        #quota_ids = []
        #lines = self._get_quota_info()
        #for q in lines:
            #_logger.info(q)
            #note += q['note']

            #quota_id = quota.browse(q['quota_id'])
            #quota_id.amount_paid += q['to_pay']
            #quota_id.date_payment = fields.Date.today()

        payment_method_id = contract.journal_id.inbound_payment_method_ids[0]
        payment_info = {
            'partner_id': self.partner_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'amount': self.monto_divisa,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_payment_id.id,
            'payment_date': self.date, #fields.Date.today(),
            'forma_pago': self.forma_pago,
            'real_estate_contract_id': self.contract_id.id,
            'payment_method_id': payment_method_id.id,
        }

        payment_id = self.env['account.payment'].create(payment_info)
        payment_id.post()
        
        #monto_letra = self.amount_word(self.amount)
        #self.quota_ids = [(5, 0, 0)]

        #l = [(0, 0, i) for i in lines]
        #self.quota_ids = l
        #self.monto_letra = monto_letra
        return payment_id

    @api.model
    def create(self, vals):
        vals['amount'] = vals['monto_divisa']/vals['tasa']
        vals['name'] = self.env['ir.sequence'].next_by_code('payment.quota')
        obj = super(PaymentQuota, self).create(vals)
        l = [(0, 0, i) for i in obj._get_quota_info()]
        obj.quota_ids = l
        return  obj


class PaymentQuotaLine(models.Model):
    _name = 'payment.quota.line'

    pago_id = fields.Many2one('payment.quota')
    quota_id = fields.Many2one('real.estate.contract.quota', string='Cuota/Descripcion')
    date_due = fields.Date(related='quota_id.date_due')
    currency_id = fields.Many2one(related='quota_id.currency_id')
    amount = fields.Monetary(currency_field='currency_id', string='Monto Cuota')
    amount_paid = fields.Monetary(currency_field='currency_id', string='Monto Pagado')
    residual = fields.Monetary(currency_field='currency_id', string='Residual')
    to_pay = fields.Monetary(currency_field='currency_id', string='A pagar')
    note = fields.Char()

