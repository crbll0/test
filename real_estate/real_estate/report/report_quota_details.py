# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _name = "real.estate.quota.details"
    _description = "Quota Details"
    _auto = False
    _rec_name = 'date'

    # @api.multi
    # @api.depends('currency_id', 'date', 'price_total', 'price_average', 'residual')
    # def _compute_amounts_in_user_currency(self):
    #     """Compute the amounts in the currency of the user
    #     """
    #     user_currency_id = self.env.user.company_id.currency_id
    #     currency_rate_id = self.env['res.currency.rate'].search([
    #         ('rate', '=', 1),
    #         '|', ('company_id', '=', self.env.user.company_id.id), ('company_id', '=', False)], limit=1)
    #     base_currency_id = currency_rate_id.currency_id
    #     for record in self:
    #         date = record.date or fields.Date.today()
    #         company = record.company_id
    #         record.user_currency_price_total = base_currency_id._convert(record.price_total, user_currency_id, company, date)
    #         record.user_currency_price_average = base_currency_id._convert(record.price_average, user_currency_id, company, date)
    #         record.user_currency_residual = base_currency_id._convert(record.residual, user_currency_id, company, date)

    contract_id = fields.Many2one('real.estate.contract', string='Contract')

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=1)
    actividad_economica = fields.Char('Actividad Economica',
        selection=[
            ('ama_de_casa', 'Ama de Casa'),
            ('privado', 'Empleado Privado'),
            ('publico', 'Empleado Publico'),
            ('ensenanzas', 'Ensenanzas'),
            ('estudiante', 'Estudiante'),
            ('pensionado', 'Juvilado/Pensionado'),
            ('pindependiente', 'Profesional Independiente'),
            ('tindependiente', 'Trabajador Independiente'),
            ('otros', 'Otros'),
        ]
    )

    tipo_cliente = fields.Char('Tipo Cliente',
        selection=[
            ('fisica', 'Persona Fisica'),
            ('juridica', 'Persona Juridica'),
            ('peps', 'PEPS'),
        ]
    )
    property_id = fields.Many2one('real.estate.property', string='Property', readonly=1)
    property_amount = fields.Monetary(currency_field='currency_id', readonly=1)
    tipo = fields.Char('Tipo Contrato', readonly=1)
    state = fields.Char('Estado', readonly=1)

    quota_name = fields.Char(string='Name/Reference', readonly=1)
    date = fields.Date(string='Fecha del Contrato', readonly=1)
    date_due = fields.Date(string='Fecha Vencimiento Cuota', readonly=1)
    date_payment = fields.Date(string='Fecha Pago Cuota', readonly=1)
    currency_id = fields.Many2one(related='contract_id.property_currency_id', string='Currency', readonly=1)
    amount = fields.Monetary(currency_field='currency_id', readonly=1)
    amount_paid = fields.Float(readonly=1)
    residual = fields.Monetary(currency_field='currency_id', readonly=1)

    _order = 'date desc'


    def _select(self):

        select_str = """
            SELECT q.id, 
            q.name as quota_name,
            q.contract_id as contract_id,
            c.date as date,
            c.partner_id as partner_id,
            c.property_id as property_id,
            c.property_amount as property_amount,
            c.tipo as tipo,
            c.state as state,
            MAX(p.date) as date_payment,
            q.date_due as date_due,
            q.amount as amount,
            SUM(l.to_pay) as amount_paid,
            (q.amount - SUM(l.to_pay)) as residual
        """
        return select_str


    def _from(self):
        from_str = """
            FROM real_estate_contract_quota q
            INNER JOIN real_estate_contract c ON q.contract_id = c.id
            INNER JOIN payment_quota_line l on l.quota_id = q.id
            INNER JOIN payment_quota p on l.pago_id = p.id

            WHERE p.state = 'done'
        """
        return from_str

    def _group_by(self):
        group_by_str = """
             GROUP BY q.id, q.name, q.contract_id, c.date, c.partner_id ,
             c.property_id, c.property_amount, c.tipo, c.state,
             q.date_payment, q.date_due, q.amount,
             q.amount_paid, q.residual
        """
        #group_by_str = ''
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s %s %s
        )""" % (
            self._table, self._select(), self._from(), self._group_by()
        ))

