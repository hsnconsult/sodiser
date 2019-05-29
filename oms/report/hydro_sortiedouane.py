# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_sortiedouane(models.AbstractModel):
    _name = 'report.oms.report_sortiedouane'

    def _etat_sortiedouane(self,decade,produit):
        iddecade = decade[0]
        idproduit = produit[0]
        cr = self.env.cr
        requete = "WITH sortie AS ( "\
                  "SELECT coalesce(sum(c.quantite),0) as qtesortie "\
                  "FROM oms_facture_ligne l, oms_facture f, oms_commande c "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idcommande = c.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM oms_decade WHERE id ="+str(iddecade)+") AND (SELECT fin FROM hydro_decade WHERE id ="+str(iddecade)+") "\
                  "AND c.idproduit = "+str(idproduit)+"  AND c.localite like '%ouaga%'), "\
                  "douane AS ( "\
                  "SELECT coalesce(sum(qtedeclaree),0) as qtedeclaree "\
                  "FROM oms_douane "\
                  "WHERE iddecade = "+str(iddecade)+" "\
                  "AND idproduit = "+str(idproduit)+") "\
                  "SELECT qtesortie, qtedeclaree, qtedeclaree-qtesortie as ecart FROM sortie, douane "
        cr.execute(requete)
        sdlines = cr.dictfetchall()
        return sdlines
    def _etat_sortiedouanedet(self,decade,produit):
        iddecade = decade[0]
        idproduit = produit[0]
        cr = self.env.cr
        requete = "SELECT f.name, f.datesortie, sum(c.quantite) as quantite "\
                  "FROM oms_facture_ligne l, oms_facture f, oms_commande c "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idcommande = c.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM hydro_decade WHERE id ="+str(iddecade)+") AND (SELECT fin FROM hydro_decade WHERE id ="+str(iddecade)+") "\
                  "AND c.idproduit = "+str(idproduit)+" AND c.localite like '%ouaga%' "\
                  "GROUP BY f.name, f.datesortie " \
                  "ORDER BY f.datesortie "
        cr.execute(requete)
        sdtlines = cr.dictfetchall()
        return sdtlines

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        sdlines = self._etat_sortiedouane(data['form']['decade'],data['form']['produit'])
        sdtlines = self._etat_sortiedouanedet(data['form']['decade'],data['form']['produit'])
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'sdlines': sdlines,
            'sdtlines': sdtlines,
        }
        return self.env['report'].render('oms.report_sortiedouane', docargs)