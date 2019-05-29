# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class oms_sortiedouane_report(models.TransientModel):
    _name = "oms.sortiedouane.report"
    _description = "Sortie Douane"

    decade = fields.Many2one('oms.decade', string='Décade',size=64, required=True)
    produit = fields.Many2one('product.template', 'Produit',size=64, required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['decade'] = data['form']['decade'] or False
        result['produit'] = data['form']['produit'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_sortiedouane', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['decade', 'produit', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_sortiedouanetot_report(models.TransientModel):
    _name = "oms.sortiedouanetot.report"
    _description = "Sortie Douane tot"

    decade = fields.Many2one('oms.decade', string='Décade',size=64, required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['decade'] = data['form']['decade'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_sortiedouanetot', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['decade', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_venteclient_report(models.TransientModel):
    _name = "oms.venteclient.report"
    _description = "Etat des ventes par client"

    debut = fields.Date('Début', required=True)
    fin = fields.Date('Fin', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['debut'] = data['form']['debut'] or False
        result['fin'] = data['form']['fin'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_venteclient', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['debut', 'fin', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_venteproduit_report(models.TransientModel):
    _name = "oms.venteproduit.report"
    _description = "Etat des ventes par produit"

    debut = fields.Date('Début', required=True)
    fin = fields.Date('Fin', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['debut'] = data['form']['debut'] or False
        result['fin'] = data['form']['fin'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_venteproduit', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['debut', 'fin', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_nonsorti_report(models.TransientModel):
    _name = "oms.nonsorti.report"
    _description = "Etat des bons non sortis"

    debut = fields.Date('Début', required=True)
    fin = fields.Date('Fin', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['debut'] = data['form']['debut'] or False
        result['fin'] = data['form']['fin'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_nonsorti', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['debut', 'fin', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_sorti_report(models.TransientModel):
    _name = "oms.sorti.report"
    _description = "Etat des bons sortis"

    debut = fields.Date('Début', required=True)
    fin = fields.Date('Fin', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['debut'] = data['form']['debut'] or False
        result['fin'] = data['form']['fin'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_sorti', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['debut', 'fin', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_sortiedouanemois_report(models.TransientModel):
    _name = "oms.sortiedouanemois.report"
    _description = "Etat des sorties douane par mois"

    mois = fields.Selection([('01', 'Janvier'), ('02', 'Février'), ('03', 'Mars'), ('04', 'Avril'),
            ('05', 'Mai'), ('06', 'Juin'), ('07', 'Juillet'), ('08', 'Août'), ('09', 'Septembre'),
            ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')], string='Mois', required=True)
    annee = fields.Char('Année', size=64, required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['mois'] = data['form']['mois'] or False
        result['annee'] = data['form']['annee'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=True).get_action(records, 'oms.report_sortiedouanemois', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['mois', 'annee', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class oms_decade_report(models.TransientModel):
    _name = "oms.decade.report"
    _description = "Etat des decades saisies"

    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=False).get_action(records, 'oms.report_decade', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)