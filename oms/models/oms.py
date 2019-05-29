# -*- coding: utf-8 -*-

import time
import math
import datetime
import odoo.addons.decimal_precision as dp

from odoo import tools
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo.osv import osv
from oms.enlettres import convlettres



class sequence(models.Model):
    _inherit = 'ir.sequence'
    last_day = fields.Date("Date précédente",default='2000-01-01')

class oms_decade(models.Model):
    _name = "oms.decade"
    _description = "Decade"

    name = fields.Char('Nom décade', size=64, select=True)
    debut = fields.Date('Début', required=True)
    fin = fields.Date('Fin', required=True)

    _sql_constraints = [
        ('name_uniq','UNIQUE(name)','La decade existe deja')
    ]

class SaleOrder(models.Model):
    _name = "sale.order"
    _description = "Sales Order"
    _inherit = "sale.order"

    @api.depends('amount_totalo')
    def compute_amount_text(self):
        return convlettres(self.amount_totals)
    @api.depends('order_line.price_subtotalo')
    def _calcule_montantht(self):
        for order in self:
            montant = 0
            for record in order.order_line:
                montant = montant + record.price_subtotalo
            order.amount_untaxedo = montant
    @api.depends('amount_tax')
    def _calcule_taxe(self):
        for order in self:
            if order.amount_tax == 0 :
               order.amount_taxo = 0
            else :
               order.amount_taxo = order.amount_untaxedo * 0.002
    @api.depends('amount_untaxedo','amount_taxo')
    def _calcule_montantttc(self):
        for order in self:
            order.amount_totalo = order.amount_untaxedo +  order.amount_taxo
    @api.depends('amount_totalo','amount_total')
    def _calcule_avoir(self):
        for order in self:
            order.amount_avoir = order.amount_totalo -order.amount_total
    @api.depends('order_line.price_subtotals')
    def _calcule_montantsttc(self):
        for order in self:
            montant = 0
            for record in order.order_line:
                montant = montant + record.price_totals
            order.amount_totals = montant
    @api.depends('confirmation_date')
    def get_datecom(self):
        for record in self:
            if record.confirmation_date:
               record.datecom = record.confirmation_date.date()
               
    def validepo(self):
        po = self.env['purchase.order'].search([('origin','=',self.name)])
        for record in po:
            if record.state == 'draft':
               for recordfil in record.order_line:
                   if self.localite == 'ouaga':
                      recordfil.price_unit = recordfil.product_id.ouaga
                   if self.localite == 'bobo':
                      recordfil.price_unit = recordfil.product_id.bobo
               record.button_approve(force=False)
               exp = self.env['stock.picking'].search([('origin','=',record.name)])
               for recordfill in exp:
                   for recordfilll in recordfill.move_lines:
                       recordfilll.quantity_done = recordfilll.product_uom_qty
                   recordfill.button_validate()
        liv = self.env['stock.picking'].search([('origin','=',self.name)])
        for recordll in liv:
            for recordlll in recordll.move_lines:
                recordlll.quantity_done = recordlll.product_uom_qty
            recordll.button_validate()
            
    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        self.validepo()
        return True
    
    localite = fields.Selection([('ouaga', 'OUAGADOUGOU'),('bobo', 'BOBO DIOULASSO'),],'Localité', default = 'ouaga')
    amount_untaxedo = fields.Monetary(string='Montant HT', store=True, readonly=True, compute='_calcule_montantht', track_visibility='always')
    amount_taxo = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_calcule_taxe', track_visibility='always')
    amount_totalo = fields.Monetary(string='Total', store=True, readonly=True, compute='_calcule_montantttc', track_visibility='always')
    amount_totals = fields.Monetary(string='Total', store=True, readonly=True, compute='_calcule_montantsttc', track_visibility='always')
    amount_avoir = fields.Monetary(string='Avoir', store=True, readonly=True, compute='_calcule_avoir', track_visibility='always')
    champvide = fields.Monetary(string='     ', size=64, select=True,readonly=True)
    datecom = fields.Date('Date com', compute='get_datecom', store=True)
    
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = 'Sales Order Line'
    _inherit = "sale.order.line"

    @api.depends('product_uom_qty')
    def compute_amount_text(self):
        return convlettres(self.product_uom_qty)
    @api.depends('product_id.name')
    def get_puofficiel(self):
        for record in self:
            record.pu_officiel = record.product_id.lst_price
    @api.depends('product_id.name','order_id.localite')
    def get_pusonabhy(self):
        for record in self:
            if record.order_id.localite == 'ouaga':
               record.pu_sonabhy = record.product_id.ouaga
            if record.order_id.localite == 'bobo':
               record.pu_sonabhy = record.product_id.bobo
    @api.depends('product_uom_qty','pu_officiel')
    def _compute_subtotalo(self):
        for record in self:
            record.price_subtotalo = record.product_uom_qty * record.pu_officiel
    @api.depends('product_uom_qty','pu_sonabhy')
    def _compute_subtotals(self):
        for record in self:
            record.price_subtotals = record.product_uom_qty * record.pu_sonabhy
            record.price_taxs = (record.product_uom_qty * record.pu_sonabhy) * 0.002
            record.price_totals = (record.product_uom_qty * record.pu_sonabhy) + (record.product_uom_qty * record.pu_sonabhy) * 0.002
    @api.depends('product_uom_qty')
    def get_pvmax(self,idproduit,idzone):
        #idzone = self.order_id.partner_id.idzone.id
        cr = self.env.cr
        cr.execute('SELECT pvm FROM oms_prixzone WHERE name=%s AND idproduit=%s',(idzone,idproduit,))
        pvm = cr.fetchone()[0]
        return pvm

    
    factures = fields.Boolean('Facturé SONABHY', default=False)
    pu_officiel = fields.Float(compute='get_puofficiel', string='Prix unitaire o', size=64, digits=(16,2), readonly=True, store=True)
    price_subtotalo = fields.Float(compute='_compute_subtotalo', string='Sous total o', readonly=True, store=True)
    pu_sonabhy = fields.Float(compute='get_pusonabhy', string='Prix unitaire s', size=64, digits=dp.get_precision('Product Price Sonabhy'), readonly=True, store=True)
    price_subtotals = fields.Float(compute='_compute_subtotals', string='Sous total s', readonly=True, store=True)
    price_totals = fields.Float(compute='_compute_subtotals', string='Sous total s ttc', readonly=True, store=True)
    price_taxs = fields.Float(compute='_compute_subtotals', string='taxe s', readonly=True, store=True)



class AccountPayment(models.Model):
    _name = 'account.payment'
    _description = 'Payments'
    _inherit = "account.payment"

    @api.depends('amount')
    def compute_text(self):
        return convlettres(self.amount)

    objet = fields.Char('Objet', size=64, select=True)

class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _description = 'Account invoice'
    _inherit = "account.invoice"

    @api.depends('amount_total')
    def compute_amount_text(self):
        return convlettres(self.amount_total)

    @api.depends('amount_avoir')
    def compute_amount_avoir_text(self):
        return convlettres(self.amount_avoir)
    
    @api.depends('invoice_line_ids.price_subtotalo')
    def _calcule_montantht(self):
        for invoice in self:
            montant = 0
            for record in invoice.invoice_line_ids:
                montant = montant + record.price_subtotalo
            invoice.amount_untaxedo = montant
    @api.depends('amount_untaxedo','amount_total','amount_untaxed')
    def _calcule_taxe(self):
        for invoice in self:
            if invoice.amount_total-invoice.amount_untaxed == 0:
               invoice.amount_taxo = 0
            else:
               invoice.amount_taxo = invoice.amount_untaxedo * 0.002
    @api.depends('amount_untaxedo','amount_taxo')
    def _calcule_montantttc(self):
        for invoice in self:
            invoice.amount_totalo = invoice.amount_untaxedo +  invoice.amount_taxo
    @api.depends('amount_totalo','amount_total')
    def _calcule_avoir(self):
        for invoice in self:
            invoice.amount_avoir = invoice.amount_totalo -invoice.amount_total
    def setprice(self):
        inv = self.env['account.invoice'].search([])
        for record in inv:
            for recordfil in record.invoice_line_ids:
                found = 0
                for pl in record.partner_id.property_product_pricelist.item_ids:
                    if recordfil.product_id.id == pl.product_tmpl_id.id:
                       #raise ValidationError(recordfil.price_unit)
                       recordfil.price_unit = pl.fixed_price
                       found = 1
                if found == 0:
                   recordfil.price_unit = pl.product_tmpl_id.list_price
            if record.amount_tax !=0:
               record.amount_tax = record.amount_untaxed*0.002
            #record.amount_total = record.amount_untaxed + record.amount_tax
            #record.amount_avoir = record.amount_totalo -invoice.amount_total
    def setdate(self):
        inv = self.env['account.invoice'].search([])
        for record in inv:
            if record.origin:               
               be = self.env['sale.order'].search([('name','=',record.origin)])
               if len(be)>0:
                  be = be[0] 
                  raise ValidationError(be.confirmation_date)
                  if be.confirmation_date == '2018-08-27 17:37:52':
                     record.date_invoice = be.confirmation_date
    amount_untaxedo = fields.Monetary(string='Montant HT', store=True, readonly=True, compute='_calcule_montantht', track_visibility='always')
    amount_taxo = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_calcule_taxe', track_visibility='always')
    amount_totalo = fields.Monetary(string='Total', store=True, readonly=True, compute='_calcule_montantttc', track_visibility='always')
    amount_avoir = fields.Monetary(string='Avoir', store=True, readonly=True, compute='_calcule_avoir', track_visibility='always')
    champvide = fields.Monetary(string='     ', size=64, select=True,readonly=True)
    numbeman = fields.Char('Numéro Bon manuel')


class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _description = 'Invoice Line'
    _inherit = "account.invoice.line"

    @api.depends('product_id.name')
    def get_puofficiel(self):
        for record in self:
            record.pu_officiel = record.product_id.lst_price
    @api.depends('quantity','pu_officiel')
    def _compute_subtotalo(self):
        for record in self:
            record.price_subtotalo = record.quantity * record.pu_officiel
    @api.depends('product_uom_qty')
    def get_pvmax(self,idproduit,idzone):
        cr = self.env.cr
        cr.execute('SELECT pvm FROM oms_prixzone WHERE name=%s AND idproduit=%s',(idzone,idproduit,))
        pvm = cr.fetchone()[0]
        return pvm
    pu_officiel = fields.Float(compute='get_puofficiel', string='Prix unitaire o', size=64, digits=(16,2), readonly=True, store=True)
    price_subtotalo = fields.Float(compute='_compute_subtotalo', string='Sous total o', readonly=True, store=True)

class ProductTemplate(models.Model):
    _name = "product.template"
    _description = "Product"
    _inherit = "product.template"
    
    ouaga =  fields.Float('Prix Achat Ouaga', size=64, digits=dp.get_precision('Product Price'))
    bobo =  fields.Float('Prix Achat Bobo', size=64, digits=dp.get_precision('Product Price'))
    ligne_prixzone = fields.One2many('oms.prixzone', 'idproduit', string='Prix zone')
    

class oms_zone(models.Model):
    _name = "oms.zone"
    _description = "Zone"

    name = fields.Char('Zone', size=64, select=True)

class oms_prixzone(models.Model):
    _name = "oms.prixzone"
    _description = "Prix Zone"

    idproduit = fields.Many2one('product.template', string='Produit', required=True)
    name = fields.Many2one('oms.zone', string='Zone', required=True)
    pvm = fields.Float('Prix de Vente Max', size=64, select=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    idzone = fields.Many2one('oms.zone', string='Zone')

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = 'account.move'

    def reouvrir(self):
        self.write({'state':'draft'})

    @api.multi
    def _get_default_journal_name(self):
        if self.env.context.get('default_journal_name'):
            return self.env['account.journal'].search([('name', '=', self.env.context['default_journal_name'])], limit=1).id
        
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'posted': [('readonly', True)]}, default=_get_default_journal_name)


   
class oms_facture(models.Model):
    _name = "oms.facture"
    _description = "Facture"
    def calcule_montant(self):
        for record in self:
            montantcal = 0
            for recordfil in record.ligne_facture:
                montantcal = montantcal+recordfil.montant
            record.montant = montantcal
    def calcule_totgasoil(self):
        for record in self:
            montantcal = 0
            for recordfil in record.ligne_facture:
                if 'GAS' in recordfil.idlcommande.product_id.name.upper():
                    montantcal = montantcal+recordfil.quantite
            record.totgasoil = montantcal
    def calcule_totsuper(self):
        for record in self:
            montantcal = 0
            for recordfil in record.ligne_facture:
                if 'SUP' in recordfil.idlcommande.product_id.name.upper():
                    montantcal = montantcal+recordfil.quantite
            record.totsuper = montantcal
    def calcule_totddo(self):
        for record in self:
            montantcal = 0
            for recordfil in record.ligne_facture:
                if 'DDO' in recordfil.idlcommande.product_id.name.upper():
                    montantcal = montantcal+recordfil.quantite
            record.totddo = montantcal
    def calcule_totpetrole(self):
        for record in self:
            montantcal = 0
            for recordfil in record.ligne_facture:
                if 'PET' in recordfil.idcommande.product_id.name.upper():
                    montantcal = montantcal+recordfil.quantite
            record.totpetrole = montantcal

    name = fields.Char('Numéro Facture', size=64, select=True)
    datefact = fields.Date('Date Facture', required=True)
    datesortie = fields.Date('Date de sortie', required=True)
    totgasoil = fields.Float(compute='calcule_totgasoil', string='Quantité Gasoil', size=64, digits=(16,2))
    totsuper = fields.Float(compute='calcule_totsuper', string='Quantité Super', size=64, digits=(16,2))
    totddo = fields.Float(compute='calcule_totddo', string='Quantité DDO', size=64, digits=(16,2))
    totpetrole = fields.Float(compute='calcule_totpetrole', string='Quantité Petrole Lampant', size=64, digits=(16,2))
    montant = fields.Float(compute='calcule_montant', string='Montant', size=64, digits=(16,0))
    state = fields.Selection([('nonreglee', 'Non réglée'),('reglee', 'Réglée'),],'Etat', readonly=True, track_visibility='onchange', default = 'nonreglee')
    ligne_facture = fields.One2many('oms.facture.ligne', 'idfacture', string='Commandes')


class oms_ligne_facture(models.Model):
    _name = "oms.facture.ligne"
    _description = "Ligne Facture"
    def create(self, vals):
        commande = self.env[('sale.order.line')].browse(vals.get('idlcommande'))
        commande.write({'factures':True})
        result = super(oms_ligne_facture,self).create(vals)
        return result
    def unlink(self):
        commande = self.idlcommande
        commande.write({'factures':False})
        result = super(oms_ligne_facture,self).unlink()
        return result
    def get_prixcourant(self,idlcommande):
        cr = self.env.cr
        res = {}
        if idlcommande :
            cr.execute('SELECT localite FROM  sale_order s, sale_order_line sl WHERE sl.order_id = s.id AND sl.id = %s ',(idlcommande,))
            localite = cr.fetchone()[0]
            requete = "SELECT "+localite+" FROM product_template p, sale_order_line sl  WHERE sl.product_id = p.id AND sl.id = %s "
            cr.execute(requete,(idlcommande,))
            prix = cr.fetchone()[0]
            #raise osv.except_osv(('Incoherence'), (idlcommande))
            res['prixl'] = prix
            res['prixlh'] = prix
        return {'value': res}
    def get_valeur_prix(self):
        for record in self:
            record.prixl = record.prixlh
    def get_quantite(self):
        for record in self:
            record.quantite = record.idlcommande.product_uom_qty
    def get_montant(self):
        for record in self:
            record.montant = record.quantite*record.prixlh

    idfacture = fields.Many2one('oms.facture', string='Facture', required=True)
    idcommande = fields.Many2one('sale.order', string='Numero de bon', required=True)
    idlcommande = fields.Many2one('sale.order.line', string='Produit', domain="[('factures','=',False)]", required=True)
    quantite = fields.Float(compute='get_quantite', string='Quantité', size=64, digits=(16,2))
    prixl =  fields.Float(compute='get_valeur_prix', string='Prix du litre',size=64)
    prixlh =  fields.Float('Prix du Litre', size=64, required=True)
    montant = fields.Float(compute='get_montant', string='Montant', size=64, digits=(16,0))



class oms_reglement(models.Model):
    _name = "oms.reglement"
    _description = "Reglement"
    def calcule_montant(self):
        for record in self:
            montantcal = 0
            for recordfil in record.ligne_reglement:
                montantcal = montantcal+recordfil.montant
            record.montant = montantcal

    datereg = fields.Date('Date Règlement', required=True)
    montant = fields.Float(compute='calcule_montant', string='Montant', size=64, digits=(16,0))
    ligne_reglement = fields.One2many('oms.reglement.ligne', 'idreglement', string='Règlements')


class oms_ligne_reglement(models.Model):
    _name = "oms.reglement.ligne"
    _description = "Ligne Reglement"
    def create(self, vals):
        facture = self.env[('oms.facture')].browse(vals.get('idfacture'))
        facture.write({'state':'reglee'})
        result = super(oms_ligne_reglement,self).create(vals)
        return result
    def unlink(self):
        facture = self.idfacture
        facture.write({'state':'nonreglee'})
        result = super(oms_ligne_reglement,self).unlink()
        return result
    def get_montant(self):
        for record in self:
            record.montant = record.idfacture.montant

    idreglement = fields.Many2one('oms.reglement', string='Reglement', required=True)
    idfacture = fields.Many2one('oms.facture', string='Numero de facture', domain="[('state','=','nonreglee')]", required=True)
    montant = fields.Float(compute='get_montant', string='Montant', size=64, digits=(16,0))

    _sql_constraints = [
        ('factreg_uniq', 'unique(idfacture,idreglement)', 'La meme facture est choisie plusieurs fois')
    ] 



class oms_douane(models.Model):
    _name = "oms.douane"
    _description = "Douane"

    name = fields.Char('Numéro Document', size=64, select=True)
    iddecade = fields.Many2one('oms.decade', string='Décade', required=True)
    idproduit = fields.Many2one('product.product', string='Produit', required=True)
    qtedeclaree = fields.Float('Quantité déclarée', required=True, digits=(16,2))
    qteliquidee = fields.Float('Quantité liquidée', required=True, digits=(16,2))
    montant = fields.Float('Montant', required=True, digits=(16,0))


class oms_vuvente(models.Model):
    _name = "oms.vuvente"
    _description = "Statistiques des ventes"
    _auto = False

    id = fields.Integer('id'),
    datebon = fields.Date('Date Bon', readonly=True)
    jour = fields.Char('Jour', readonly=True)
    mois = fields.Selection([('01', 'Janvier'), ('02', 'Février'), ('03', 'Mars'), ('04', 'Avril'),
            ('05', 'Mai'), ('06', 'Juin'), ('07', 'Juillet'), ('08', 'Août'), ('09', 'Septembre'),
            ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')], 'Mois', readonly=True)
    trimestre = fields.Char('Trimestre', readonly=True)
    annee = fields.Char('Annee', readonly=True)
    numbon = fields.Char('Numéro Bon', readonly=True)
    client = fields.Char('Client', readonly=True)
    localite = fields.Char('Localité', readonly=True)
    produit = fields.Char('Produit', readonly=True)
    montant = fields.Integer('Chiffre Affaire', readonly=True)
    volume = fields.Integer('Volume', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'oms_vuvente')
        requete = "CREATE or REPLACE VIEW oms_vuvente AS( " \
                  "SELECT row_number() over(order by c.confirmation_date) as id, c.confirmation_date::date as datebon, c.name as numbon, cl.name as client, c.localite as localite, p.name as produit, l.product_uom_qty as volume, l.price_total as montant, " \
                                                                                          "to_char(c.confirmation_date,'dd-mm-yyyy') as jour, " \
                                                                                          "to_char(c.confirmation_date,'mm') as mois, " \
                                                                                          "to_char(c.confirmation_date,'yyyy') as annee, " \
                                                                                          "CASE WHEN to_char(c.confirmation_date,'mm') IN ('01','02','03') THEN '1er trimestre' " \
                                                                                               "WHEN to_char(c.confirmation_date,'mm') IN ('04','05','06') THEN '2eme trimestre' " \
                                                                                               "WHEN to_char(c.confirmation_date,'mm') IN ('07','08','09') THEN '3eme trimestre' " \
                                                                                               "WHEN to_char(c.confirmation_date,'mm') IN ('10','11','12') THEN '4eme trimestre' " \
                                                                                          "END as trimestre " \
                  "FROM sale_order c " \
                  "LEFT JOIN sale_order_line l " \
                  "ON l.order_id = c.id " \
                  "LEFT JOIN product_template p " \
                  "ON l.product_id = p.id " \
                  "LEFT JOIN res_partner cl " \
                  "ON c.partner_id = cl.id " \
                  "ORDER BY c.confirmation_date)"
        self.env.cr.execute(requete)


class oms_commande(models.Model):
    _name = "oms.commande"
    _description = "Vue des commandes"
    _auto = False

    id = fields.Integer('id'),
    idcom = fields.Integer('idcom'),
    numbon = fields.Char('Numero', size=64, required=True)
    datebon = fields.Date('Date du bon', size=64, required=True)
    idclient = fields.Many2one('hydro.client', string='Client', size=64, required=True)
    idproduit = fields.Many2one('hydro.produit', string='Produit',size=64, required=True)
    localite = fields.Char('Localite',size=64, required=True)
    quantite = fields.Float('Quantite', required=True, digits=(16,2), size=64)
    montant = fields.Float('Montant', required=True, size=64, digits=(16,0))
    factureh = fields.Boolean('Facturé')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'oms_commande')
        requete = "CREATE or REPLACE VIEW oms_commande AS( " \
                  "SELECT row_number() over(order by c.confirmation_date) as id, l.id as idcom, c.confirmation_date::date as datebon, c.name as numbon, cl.id as idclient, c.localite as localite, p.id as idproduit, l.product_uom_qty as quantite, l.price_total as montant, l.factures as factureh, " \
                                                                                          "to_char(c.confirmation_date,'dd-mm-yyyy') as jour, " \
                                                                                          "to_char(c.confirmation_date,'mm') as mois, " \
                                                                                          "to_char(c.confirmation_date,'yyyy') as annee, " \
                                                                                          "CASE WHEN to_char(c.confirmation_date,'mm') IN ('01','02','03') THEN '1er trimestre' " \
                                                                                               "WHEN to_char(c.confirmation_date,'mm') IN ('04','05','06') THEN '2eme trimestre' " \
                                                                                               "WHEN to_char(c.confirmation_date,'mm') IN ('07','08','09') THEN '3eme trimestre' " \
                                                                                               "WHEN to_char(c.confirmation_date,'mm') IN ('10','11','12') THEN '4eme trimestre' " \
                                                                                          "END as trimestre " \
                  "FROM sale_order c " \
                  "LEFT JOIN sale_order_line l " \
                  "ON l.order_id = c.id " \
                  "LEFT JOIN product_template p " \
                  "ON l.product_id = p.id " \
                  "LEFT JOIN res_partner cl " \
                  "ON c.partner_id = cl.id " \
                  "ORDER BY c.confirmation_date)"
        self.env.cr.execute(requete)

class oms_vuclient(models.Model):
    _name = "oms.vuclient"
    _description = "Etats des clients"
    _auto = False

    id = fields.Integer('id'),
    dateop = fields.Date('Date Opération', readonly=True)
    jour = fields.Char('Jour', readonly=True)
    mois = fields.Selection([('01', 'Janvier'), ('02', 'Février'), ('03', 'Mars'), ('04', 'Avril'),
            ('05', 'Mai'), ('06', 'Juin'), ('07', 'Juillet'), ('08', 'Août'), ('09', 'Septembre'),
            ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')], 'Mois', readonly=True)
    trimestre = fields.Char('Trimestre', readonly=True)
    annee = fields.Char('Annee', readonly=True)
    reference = fields.Char('Référence', readonly=True)
    idclient = fields.Many2one('res.partner', string='Client', readonly=True)
    typeop = fields.Char('Type', readonly=True)
    montantcom = fields.Integer('Montant commande', readonly=True)
    montantpaie = fields.Integer('Montant réglé', readonly=True)
    solde = fields.Integer('Solde', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'oms_vuclient')
        requete = "CREATE or REPLACE VIEW oms_vuclient AS( " \
                  "WITH commande as  " \
                  "(SELECT confirmation_date::date as dateop, partner_id as idclient, name as reference, 'commande'::varchar as typeop, amount_total as montantcom, 0 as montantpaie, " \
                                                                                          "to_char(confirmation_date,'dd-mm-yyyy') as jour, " \
                                                                                          "to_char(confirmation_date,'mm') as mois, " \
                                                                                          "to_char(confirmation_date,'yyyy') as annee, " \
                                                                                          "CASE WHEN to_char(confirmation_date,'mm') IN ('01','02','03') THEN '1er trimestre' " \
                                                                                               "WHEN to_char(confirmation_date,'mm') IN ('04','05','06') THEN '2eme trimestre' " \
                                                                                               "WHEN to_char(confirmation_date,'mm') IN ('07','08','09') THEN '3eme trimestre' " \
                                                                                               "WHEN to_char(confirmation_date,'mm') IN ('10','11','12') THEN '4eme trimestre' " \
                                                                                          "END as trimestre " \
                  "FROM sale_order WHERE state in ('sale','done')), " \
                  "reglement as " \
                  "(SELECT payment_date::date as dateop, partner_id as idclient, name as reference, 'reglement'::varchar as typeop, 0 as montantcom, amount as montantpaie, " \
                                                                                          "to_char(payment_date,'dd-mm-yyyy') as jour, " \
                                                                                          "to_char(payment_date,'mm') as mois, " \
                                                                                          "to_char(payment_date,'yyyy') as annee, " \
                                                                                          "CASE WHEN to_char(payment_date,'mm') IN ('01','02','03') THEN '1er trimestre' " \
                                                                                               "WHEN to_char(payment_date,'mm') IN ('04','05','06') THEN '2eme trimestre' " \
                                                                                               "WHEN to_char(payment_date,'mm') IN ('07','08','09') THEN '3eme trimestre' " \
                                                                                               "WHEN to_char(payment_date,'mm') IN ('10','11','12') THEN '4eme trimestre' " \
                                                                                          "END as trimestre " \
                  "FROM account_payment WHERE state <> 'draft'), " \
                  "operations as( " \
                  "(SELECT dateop, idclient, reference, typeop, montantcom, montantpaie, jour, mois, annee, trimestre  FROM commande) UNION ALL (SELECT dateop, idclient, reference, typeop, montantcom, montantpaie, jour, mois, annee, trimestre FROM reglement) ORDER BY dateop) " \
                  "SELECT row_number() over(order by dateop) as id, dateop, idclient, reference, typeop, montantcom, montantpaie, montantpaie-montantcom as solde, jour, mois, annee, trimestre " \
                  "FROM operations ORDER BY dateop)"
        self.env.cr.execute(requete)


class Company(models.Model):
    _name = "res.company"
    _description = 'Companies'
    _inherit = "res.company"

    
    arretecom = fields.Text('Arrêté 1')
    arretefact = fields.Text('Arrêté 2')
