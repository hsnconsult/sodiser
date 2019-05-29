# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_sortiedouanetot(models.AbstractModel):
    _name = 'report.oms.report_sortiedouanetot'

    def _etat_sortiedouanetot(self,decade):
        iddecade = decade[0]
        cr = self.env.cr
        requete = "WITH sortie AS ( "\
                  "SELECT p.name as produit, coalesce(qtesortie,0) as qtesortie , coalesce(montant,0) as montant "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(c.quantite),0) as qtesortie, coalesce(sum(c.montant),0) as montant "\
                  "FROM oms_facture_ligne l, oms_facture f, oms_commande c, product_template p "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idlcommande = c.idcom "\
                  "AND c.idproduit = p.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM oms_decade WHERE id ="+str(iddecade)+") AND (SELECT fin FROM oms_decade WHERE id ="+str(iddecade)+") "\
                  "AND c.localite like '%ouaga%' GROUP BY p.name) com ON com.produit = p.name), "\
                  "douane AS ( "\
                  "SELECT p.name as produit, coalesce(qtedeclaree,0) as qtedeclaree "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(d.qtedeclaree),0) as qtedeclaree "\
                  "FROM oms_douane d, product_template p "\
                  "WHERE d.iddecade = "+str(iddecade)+" AND d.idproduit = p.id "\
                  "GROUP BY p.name) douane ON douane.produit = p.name) "\
                  "SELECT p.name as produit, s.qtesortie, d.qtedeclaree, d.qtedeclaree-s.qtesortie as ecart, s.montant FROM product_template p "\
                  "LEFT JOIN sortie s "\
                  "ON s.produit = p.name "\
                  "LEFT JOIN douane d "\
                  "ON d.produit = p.name "\
                  "ORDER BY p.name"
        cr.execute(requete)
        sdlines = cr.dictfetchall()
        return sdlines
    def _etat_sortiedouanetotdet(self,decade):
        iddecade = decade[0]
        cr = self.env.cr
        requete = "SELECT p.name as produit, f.name, f.datesortie, sum(sol.product_uom_qty) as quantite, sum(sol.price_total) as montant "\
                  "FROM oms_facture_ligne l, oms_facture f,  product_template p, sale_order so, sale_order_line sol "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idcommande = so.id "\
                  "AND l.idlcommande = sol.id "\
                  "AND sol.product_id = p.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM oms_decade WHERE id ="+str(iddecade)+") AND (SELECT fin FROM oms_decade WHERE id ="+str(iddecade)+") "\
                  "AND so.localite like '%ouaga%' "\
                  "GROUP BY p.name, f.name, f.datesortie " \
                  "ORDER BY p.name, f.datesortie "
        cr.execute(requete)
        sdtlines = cr.dictfetchall()
        return sdtlines
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        sdlines = self._etat_sortiedouanetot(data['form']['decade'])
        sdtlines = self._etat_sortiedouanetotdet(data['form']['decade'])
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'sdlines': sdlines,
            'sdtlines': sdtlines,
        }
        return self.env['report'].render('oms.report_sortiedouanetot', docargs)