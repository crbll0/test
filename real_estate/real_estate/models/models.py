# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from num2words import num2words

_logger = logging.getLogger(__name__)

READONLY_STATE_PROPERTY = {'available': [('readonly', False)]}
READONLY_STATE = {'draft': [('readonly', False)]}

value = "Un apartamento denominado Unidad Funcional No. ___, \
identificada como ____: __, matrícula No. _____, (SP-________), \
localizado en el Nivel __ del Bloque 0_, del Condominio \
 Residencial Palmera Oriental Etapa 4, Santo Domingo Este, \
 con una extensión superficial de (________ mts2), \
 más un parqueo de (12.00mts2), (SP-00-01-_________)"


class RealEstateProject(models.Model):
    _name = 'real.estate.project'
    _description = 'Real Estate Project'

    @api.depends('property_ids')
    def _count_property(self):
        for i in self:
            i.count_property = len(i.property_ids)
            i.count_property_available = len([a for a in i.property_ids])

    name = fields.Char('Nombre del Projecto', required=1)
    street = fields.Char('street')
    street2 = fields.Char('street 2')
    city = fields.Char('CIty')
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]",
                                ondelete='restrict')
    country_id = fields.Many2one('res.country', readonly=1,
                                 ondelete='restrict',
                                 default = lambda self: self.env.user.company_id.country_id.id)

    etapa = fields.Char('Etapa')
    description = fields.Text('Descripcion')
    property_ids = fields.One2many('real.estate.property', 'project_id')
    count_property = fields.Integer(compute='_count_property')
    count_property_available = fields.Integer(compute='_count_property')
    designacion_catastral = fields.Char(string='Designacion Cartastral')
    matricula = fields.Char(string='Matricula')
    metraje = fields.Float(string='Metraje')
    company_id = fields.Many2one('res.company', string='Compania', default=lambda self: self.env.user.company_id.id)
    
    @api.multi
    def action_open_properties(self):
        actions = {
            "name": "Propiedades",
            "type": "ir.actions.act_window",
            "res_model": "real.estate.property",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", [i.id for i in self.property_ids]]],
        }

        return actions


class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'Real State Property'

    name = fields.Char(string='Nombre', compute='_compute_name', store=1)
    code = fields.Char(string='Codigo', readonly=1, states=READONLY_STATE_PROPERTY)
    amount = fields.Monetary(string='Valor de la Propiedad', required=1, readonly=1,
                          states=READONLY_STATE_PROPERTY, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=1, readonly=1,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  states=READONLY_STATE_PROPERTY)

    company_id = fields.Many2one('res.company', string='Compania', states=READONLY_STATE_PROPERTY, default=lambda self: self.env.user.company_id.id)
    property_type = fields.Many2one('real.estate.property.type',
                                    string='Tipo de Propiedad', required=1,
                                    readonly=1, states=READONLY_STATE_PROPERTY, ondelete='restrict')
    street = fields.Char('Calle', readonly=1, states=READONLY_STATE_PROPERTY)
    street2 = fields.Char('CAlle 2', readonly=1, states=READONLY_STATE_PROPERTY)
    city = fields.Char('Ciudad', readonly=1, states=READONLY_STATE_PROPERTY)
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]",
                               readonly=1, states=READONLY_STATE_PROPERTY, ondelete='restrict')
    country_id = fields.Many2one('res.country', readonly=1, states=READONLY_STATE_PROPERTY,
                                 ondelete='restrict',
                                 default = lambda self: self.env.user.company_id.country_id.id)
    state = fields.Selection([
        ('available', 'Disponible'),
        ('reserved', 'Reservado'),
        ('sold', 'Vendido'),
    ], default='available', string='State',
        help=" * The 'Available' status is used when a user is encoding a new property.\n"
             " * The 'Reserved' status is used when user creates a contract and validate it.\n"
             " * The 'Sold' status is set automatically when the Contract is paid.\n"
    )
    edificio = fields.Char('Edificio', readonly=1, states=READONLY_STATE_PROPERTY)
    apto = fields.Char('Apartamento #', readonly=1, states=READONLY_STATE_PROPERTY)
    separacion = fields.Monetary(string='Separacion', readonly=1, currency_field='currency_id' ,
                              states=READONLY_STATE_PROPERTY)
    project_id = fields.Many2one('real.estate.project', string='Projecto')
    rooms = fields.Integer('Numero de Habitaciones', readonly=1, states=READONLY_STATE_PROPERTY)
    bathrooms = fields.Float('Numero de Banos', readonly=1, states=READONLY_STATE_PROPERTY)
    parking = fields.Integer('Numero de Parqueos', readonly=1, states=READONLY_STATE_PROPERTY)
    floor = fields.Integer('Piso/Nivel', readonly=1, states=READONLY_STATE_PROPERTY)
    mt2 = fields.Float('Terreno Mt2', readonly=1, states=READONLY_STATE_PROPERTY)

    titulo_matricula = fields.Char(string='Matricula')
    titulo_folio = fields.Char(string='Folio')
    titulo_libro = fields.Char(string='Libro')
    titulo_fecha = fields.Date(string='Fecha')

    description = fields.Text('Description', readonly=1, states=READONLY_STATE_PROPERTY, default=value
                              )

    @api.onchange('project_id')
    def onchange_project_id(self):
        return {'value': {
            'street': self.project_id.street,
            'street2': self.project_id.street2,
            'city': self.project_id.city,
            'state_id': self.project_id.state_id.id,
            'country_id': self.project_id.country_id.id,
        }}

        # self.street = self.project_id.street
        # self.street2 = self.project_id.street2
        # self.city = self.project_id.city
        # self.state_id = self.project_id.state_id.id
        # self.country_id = self.project_id.country_id.id



    @api.depends('project_id.name', 'edificio', 'apto', 'property_type')
    def _compute_name(self):
        for record in self:
            name = '{proy} {edif} {apto} [{type}]'.format(
                proy=(record.project_id.name + ', ' if record.project_id else ''),
                edif=('Edif.' + record.edificio + ',' if record.edificio else ''),
                apto=('Apto.' + record.apto + ', ' if record.apto else ''),
                type=(record.property_type.name if record.property_type else '')
            )
            record.name = name

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('real.estate.property')
        vals['code'] = seq

        return super(RealEstateProperty, self).create(vals)

    @api.multi
    def unlink(self):
        for r in self:
            if r.state != 'available':
                raise UserError('You can not delete a property that is Reserved or sold.')
        return super(RealEstateProperty, self).unlink()


class RealEstateContractStage(models.Model):
    _name = 'real.estate.contract.stage'
    _description = 'Real Estate Contract Stage'

    name = fields.Char('Nombre de la Etapa')


class RealEstateContract(models.Model):
    _name = 'real.estate.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Real State Partner Contract'

    def format_fecha(self, fecha):
        f = fields.Date.to_date(fecha)
        r = "{:%d-%m-%Y}".format(f)
        return r

    def format_monto(self, num):
        return '{:,.2f}'.format(num)

    def date_word(self, date, with_number=False):
        if not date:
            return ''

        meses = {
            1: 'Enero',
            2: 'Febrero',
            3: 'Marzo',
            4: 'Abril',
            5: 'Mayo',
            6: 'Junio',
            7: 'Julio',
            8: 'Agosto',
            9: 'Septiembre',
            10: 'Octubre',
            11: 'Noviembre',
            12: 'Dicciembre',
        }

        day = self.number_word(date.day, currency=False, with_number=True, formato=False, upper=False)
        month = meses.get(date.month, '')
        _logger.info(('MES', date.month, meses.get(date.month, ''), month ))
        year = self.number_word(date.year, currency=False, with_number=True, formato=False, upper=False)

        word = u'dia {dia} del mes de {mes} del año {anio}'.format(
            dia=day, mes=month, anio=year
        )

        return word

    def number_word(self, numero, currency=True, with_number=True, formato=True, upper=True):
        monedas = {
            'DOP': 'PESOS DOMINICANOS',
            'EUR': 'EUROS',
            'USD': 'DOLARES ESTADOUNIDENSE'
        }

        moneda = ''
        if currency:
            moneda = monedas.get(self.property_currency_id.name, '')

        amt_lst = str('{0:.2f}'.format(numero)).split('.')

        monto_en_letras = num2words(int(amt_lst[0]), lang='es')
        numero = '{:,.2f}'.format(numero) if formato else numero
        palabra = '{monto} {moneda} ({simbolo}{numero})'.format(
            monto=monto_en_letras,
            numero=numero if with_number else '',
            moneda=moneda,
            simbolo = self.property_currency_id.symbol if currency else ''
        )
        palabra = palabra.upper() if upper else palabra
        return palabra

    def get_property_amount_word(self):
        res = self.number_word(self.property_amount, 1, 1, 1, 1)
        _logger.warning(('AQUI', res))
        return res

    def payments(self):
        r = self.env['account.payment'].search([('real_estate_contract_id', '=', self.id)])
        return r

    def zip_comodidades(self):
        def fill(lst, n):
            _logger.info((lst,'listaaa'))
            for i in range(n):
                lst.append('')
            return lst

        lst_property = ['* ' + i.name for i in self.property_id.mod_cons_ids]
        lst_project = ['* ' + i.name for i in self.property_id.project_id.mod_cons_ids]

        len_lst_property = len(lst_property)
        len_lst_project = len(lst_project)

        n = abs(len_lst_project-len_lst_property)
        if n:
            if len_lst_property > len_lst_project:
                fill(lst_project, n)
            elif len_lst_project > len_lst_property:
                fill(lst_property, n)

        return zip(lst_property, lst_project)

    @api.depends('quota_ids')
    def _count_payment_done(self):
        for r in self:
            qty_paid = 0
            for c in r.quota_ids:
                if c.residual == 0:
                    qty_paid += 1
            r.payment_done = qty_paid

    @api.depends('quota_ids.residual')
    def compute_remaining(self):
        for i in self:
            i.remaining = sum([quota.residual for quota in i.quota_ids])

    name = fields.Char(string='Nombre/Referencia', readonly=1, copy=False)

    partner_id = fields.Many2one('res.partner', string='Comprador', readonly=1,
                                 states=READONLY_STATE, ondelete='restrict')

    partner2_id = fields.Many2one('res.partner', string='Co-Comprador', readonly=1,
                                 states=READONLY_STATE)
    company_id = fields.Many2one('res.company', string='Compania',states=READONLY_STATE, default=lambda self: self.env.user.company_id.id)
    vendedor_id = fields.Many2one('res.users', string='Vendedor', readonly=1, states=READONLY_STATE)
    representante_id = fields.Many2one('res.users', string='Representante', default=lambda self: self.env.user.id, readonly=1, states=READONLY_STATE)

    property_id = fields.Many2one('real.estate.property', string='Propiedad',
                                  readonly=1, states=READONLY_STATE,
                                  ondelete='restrict')
    property_amount = fields.Monetary(related='property_id.amount', store=1,
                                      currency_field='property_currency_id')
    payment_month = fields.Monetary(currency_field='property_currency_id')
    tipo = fields.Selection([
        ('efectivo', 'Efectivo'),
        ('financiamiento', 'Financiamiento'),
    ], default='efectivo', string='Tipo de Contrato', states=READONLY_STATE)

    payment_done = fields.Integer(compute='_count_payment_done', string='Cuotas Pagadas')
    property_currency_id = fields.Many2one(related='property_id.currency_id')

    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('validate', 'Contrato Promesa'),
        ('done', 'Contrato Definitivo'),
        ('cancel', 'Desistido'),
    ], default='draft', group_expand='_read_group_stage_ids')

    advance = fields.Monetary(string='Inicial', readonly=1, states=READONLY_STATE,
                              currency_field='property_currency_id')

    lead_id = fields.Many2one('crm.lead', string='Oportunidad/Lead', states=READONLY_STATE)
    journal_id = fields.Many2one('account.journal', string='Diario de Pagos',
                                 default=lambda self: self.env.user.company_id.real_estate_journal.id,
                                 readonly=1, states=READONLY_STATE)
    remaining = fields.Monetary(string='Monto Restante', compute='compute_remaining',
                             currency_field='property_currency_id')
    date_done = fields.Date(string='Fecha de Entrega', readonly=1, states=READONLY_STATE)
    date = fields.Date(string='Fecha', readonly=1, states=READONLY_STATE, default=fields.Date.today())
    date_start = fields.Date(string='Fecha Comienzo de Cuotas', readonly=1, states=READONLY_STATE)
    separacion = fields.Monetary(string='Separacion', readonly=1,
                                 related='property_id.separacion',
                                 currency_field='property_currency_id')
    num_payments = fields.Integer(string='Numero de Cuotas', readonly=1,
                                  states=READONLY_STATE)
    len_cuotas = fields.Integer(compute='len_cuota', store=1)
    invoice_nc = fields.Many2one('account.invoice', string='Nota de Credito')
    quota_ids = fields.One2many('real.estate.contract.quota', 'contract_id')

    @api.depends('quota_ids')
    def len_cuota(self):
        for r in self:
            r.len_cuotas = len(r.quota_ids)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        _logger.info((stages, domain, order))
        stage_ids = self._search([('state', 'in', ['draft', 'validate', 'done', 'cancel'])])
        return ['draft', 'validate', 'done', 'cancel'] #self.browse(stage_ids)

    @api.onchange('property_id')
    def onchange_property(self):
        self.advance = self.property_amount * 0.20

    @api.multi
    def get_quota(self):
        if self.num_payments >= 1 and self.date_start:
            self.quota_ids.unlink()

            try:
                payment_month = abs((self.advance - self.separacion) / self.num_payments)

            except ZeroDivisionError:
                payment_month = self.num_payments

            date = self.date_start
            quota_name = _('Cuota')
            active_id = self.id

            quota_list = [(0, 0, {
                'contract_id': active_id,
                'name': 'Separacion',
                'date': date,
                'date_due': date,
                'amount': self.separacion,
            })]

            for i in range(1, self.num_payments+1):
                quota_list.append(
                    (0, 0, {
                        'contract_id': active_id,
                        'name': "%s %s" % (quota_name, i),
                        'date': date,
                        'date_due': fields.Date.add(date, months=1),
                        'amount': payment_month,
                    })
                )

                date = fields.Date.add(date, months=1)

            f1 = fields.Date.add(date, months=1)
            quota_list.append(
                (0, 0, {
                    'contract_id': active_id,
                    'name': "Cuota Final",
                    'date': f1,#fields.Date.add(date, months=1),
                    'date_due': fields.Date.add(f1, months=1),
                    'amount': self.property_amount - self.advance,
                })
            )

            self.payment_month = payment_month
            self.quota_ids = quota_list

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('real.estate.contract')
        vals['name'] = seq

        return super(RealEstateContract, self).create(vals)

    @api.multi
    def write(self, vals):
        r = super(RealEstateContract, self).write(vals)

        if vals.get('state', False) and vals['state'] == 'validate':
            pass
            # self.action_validate()
            # if not self.quota_ids:
            #     raise UserError('Necesitas indicar al menos una cuota')
            #
            # if self.property_id.state != 'available':
            #     raise UserError('Esta Propiedad no esta dispobible')
            #
            # quota_total = sum([quota.amount for quota in self.quota_ids])
            #
            # if (quota_total) != self.property_amount:
            #     raise UserError('Check the quota and advance amount.')

        if vals.get('state', False) and vals['state'] == 'done' and self.remaining != 0:
            raise UserError('Debes de Saldar el contrato para poder pasarlo a esta etapa.')

        if vals.get('state', False) and vals['state'] == 'cancel':
            self.action_cancel()

        return r

    @api.multi
    def action_open_invoices(self):
        actions = {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["communication", "=", self.name]],
        }

        return actions

    @api.multi
    def create_invoice(self):
        for i in self.quota_ids:
            i.create_invoice()

        self.invoiced = True

    @api.multi
    def action_validate(self):
        if not self.quota_ids:
            raise UserError('Necesitas indicar al menos una cuota')

        if self.property_id.state != 'available':
            _logger.info(('estado',

            self.property_id.state))
            raise UserError('Esta Propiedad no esta dispobible')

        quota_total = sum([quota.amount for quota in self.quota_ids])

        #if (quota_total ) != self.property_amount + self.separacion:
            #raise UserError('Check the quota and advance amount.')

        if self.lead_id:
            self.lead_id.action_set_won_rainbowman()

        # payment_method_id = self.journal_id.inbound_payment_method_ids[0]
        #
        # payment_data = {
        #     'payment_type': 'inbound',
        #     'partner_type': 'customer',
        #     'partner_id': self.partner_id.id,
        #     'amount': self.advance,
        #     'currency_id': self.property_currency_id.id,
        #     'journal_id': self.journal_id.id,
        #     'payment_date': self.date_start,
        #     'communication': 'Advance Contract %s' % self.name,
        #     'payment_method_id': payment_method_id.id,
        # }
        #
        # payment = self.env['account.payment'].create(payment_data)
        # self.payment_id = payment

        self.property_id.state = 'reserved'
        return self.write({'state': 'validate','date': fields.Date.today()})

    @api.multi
    def action_create_nc(self):
        action = {
            "type": "ir.actions.act_window",
            "res_model": "wizard.contract.cancel",
            "views": [[False, "form"]],
            'view_type': 'form',
            'view_mode': 'form',
            "target": "new",
        }

        return action

    @api.multi
    def action_cancel(self):
        # TODO: crear un Wizard para indicar el motivo
        #  de la cancelacion y un monto administrativo

        #_logger.info(('LLamara a Wizard Nota de Credito'))
        #self.action_create_nc()
        #_logger.info(('LLamo a Wizard Nota de Credito'))

        #action = {
            #"type": "ir.actions.act_window",
            #"res_model": "wizard.contract.cancel",
            #"views": [[False, "form"]],
            #'view_type': 'form',
            #'view_mode': 'form',
            #"target": "new",
        #}
        
        #self.state = 'cancel'
        #self.property_id.state = 'available'

        #return action
        self.property_id.state = 'available'
        return self.write({'state': 'cancel'})


class ReaLEstateContractQuota(models.Model):
    _name = 'real.estate.contract.quota'
    _description = 'Real State Contract Quota'

    # @api.depends('invoice_id', 'invoice_id.payment_move_line_ids')
    # def get_amount_paid(self):
    #     for i in self:
    #         inv = i.invoice_id
    #         total_paid = 0
    #         for payment in inv._get_payments_vals():
    #             total_paid += payment['amount']
    #
    #         i.amount_paid = total_paid
    #         i.residual = i.amount - total_paid]

    @api.depends('amount', 'amount_paid')
    def calc_residual(self):
        pagos_line = self.env['payment.quota.line']
        for o in self:
            pagos = pagos_line.search([
                            ('quota_id', '=', o.id),
                            ('pago_id.state', '=', 'done')
                        ])
            amount = sum([i.to_pay for i in pagos])
            
            o.amount_paid = amount
            o.residual = o.amount - amount if amount else o.amount
            

    #@api.depends('date')
    def get_date_due(self):
        for i in self:
            if i.date:
                i.date_due = fields.Date.add(i.date, months=1)
                
    def get_paid_amount(self):
        pagos_line = self.env['payment.quota.line']
        for o in self:
            pagos = pagos_line.search([
                            ('quota_id', '=', o.id),
                            ('pago_id.state', '=', 'done')
                        ])
            amount = sum([i.to_pay for i in pagos])
            _logger.info(('pagado',amount, pagos, o.id, o.name))
            
            o.amount_paid = o.amount - amount

    contract_id = fields.Many2one('real.estate.contract', string='Contract')

    name = fields.Char(string='Cuota/Descripcion', copy=False)
    payment_id = fields.Many2one('account.payment', string='Pago')
    date = fields.Date(string='Facha')
    date_due = fields.Date(string='Fecha Vencimiento') #compute='get_date_due', store=1)
    date_payment = fields.Date(string='Fecha del Pago')
    currency_id = fields.Many2one(related='contract_id.property_currency_id', string='Moneda')
    amount = fields.Monetary(currency_field='currency_id', string='Monto')
    amount_paid = fields.Monetary(currency_field='currency_id', string='Monto Pagado', compute='calc_residual')#, store=1)
    residual = fields.Monetary(currency_field='currency_id', compute='calc_residual')

    @api.multi
    def create_invoice(self):
        invoice_obj = self.env['account.invoice']

        product = self.env.ref('real_estate.product_quota')
        account_id = getattr(product, 'property_account_income_id')
        account_categ_id = getattr(product.categ_id, 'property_account_income_categ_id')

        contract_id = self.contract_id

        invoice_data = {
            'partner_id': contract_id.partner_id.id,
            'currency_id': contract_id.property_currency_id.id,
            'date_invoice': self.date,
            'date_due': self.date_due,
            'origin': contract_id.name,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product.id,
                    'name': self.name,
                    'account_id': account_id.id or account_categ_id.id,
                    'quantity': 1,
                    'invoice_line_tax_ids': [(4, tax.id) for tax in product.taxes_id],
                    'price_unit': self.amount,
                })
            ]
        }

        invoice = invoice_obj.create(invoice_data)

        self.invoice_id = invoice.id

    @api.model
    def cron_validate_invoice(self):
        date = fields.Date.today()

        quota_objs = self.env['real.estate.contract.quota'].search([
            ('state', '=', 'draft'),
            ('date', '=', date),
        ])

        for i in quota_objs:
            i.invoice_id.action_invoice_open()

        _logger.info((date, quota_objs))


class RealEstatePropertyType(models.Model):
    _name = 'real.estate.property.type'
    _description = 'Real State Property Type'

    name = fields.Char(string='Name/Reference', required=1, copy=False)


