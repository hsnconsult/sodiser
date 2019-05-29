# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_sortiedouanemois(models.AbstractModel):
    _name = 'report.oms.report_sortiedouanemois'

    def _etat_sortiedouanemois(self,mois,annee):
        cr = self.env.cr
        # récupération des décades
        found = 1
        reqdec = "SELECT id FROM oms_decade WHERE debut = '"+annee+"-"+mois+"-01'"
        cr.execute(reqdec)
        result = cr.fetchone()
        if result:
           dec1 = result[0]
        else:
            found = 0
            dec1 = 0
        reqdec = "SELECT id FROM oms_decade WHERE debut = '"+annee+"-"+mois+"-11'"
        cr.execute(reqdec)
        result = cr.fetchone()
        if result:
           dec2 = result[0]
        else:
            found = 0
            dec2 = 0
        reqdec = "SELECT id FROM oms_decade WHERE debut = '"+annee+"-"+mois+"-21'"
        cr.execute(reqdec)
        result = cr.fetchone()
        if result:
           dec3 = result[0]
        else:
            found = 0
            dec3 = 0
        requete = "WITH sortie1 AS ( "\
                  "SELECT p.name as produit, coalesce(qtesortie,0) as qtesortie "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(c.quantite),0) as qtesortie "\
                  "FROM oms_facture_ligne l, oms_facture f, oms_commande c, product_template p "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idlcommande = c.idcom "\
                  "AND c.idproduit = p.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM oms_decade WHERE id ="+str(dec1)+") AND (SELECT fin FROM oms_decade WHERE id ="+str(dec1)+") "\
                  "AND c.localite like '%ouaga%' GROUP BY p.name) com ON com.produit = p.name), "\
                  "douane1 AS ( "\
                  "SELECT p.name as produit, coalesce(qtedeclaree,0) as qtedeclaree "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(d.qtedeclaree),0) as qtedeclaree "\
                  "FROM oms_douane d, product_template p "\
                  "WHERE d.iddecade = "+str(dec1)+" AND d.idproduit = p.id "\
                  "GROUP BY p.name) douane ON douane.produit = p.name), "\
                  "decade1 AS ( " \
                  "SELECT p.name as produit, s.qtesortie, d.qtedeclaree, d.qtedeclaree-s.qtesortie as ecart FROM product_template p "\
                  "LEFT JOIN sortie1 s "\
                  "ON s.produit = p.name "\
                  "LEFT JOIN douane1 d "\
                  "ON d.produit = p.name "\
                  "ORDER BY p.name ), "\
                  "sortie2 AS ( "\
                  "SELECT p.name as produit, coalesce(qtesortie,0) as qtesortie "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(c.quantite),0) as qtesortie "\
                  "FROM oms_facture_ligne l, oms_facture f, oms_commande c, product_template p "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idlcommande = c.idcom "\
                  "AND c.idproduit = p.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM oms_decade WHERE id ="+str(dec2)+") AND (SELECT fin FROM oms_decade WHERE id ="+str(dec2)+") "\
                  "AND c.localite like '%ouaga%' GROUP BY p.name) com ON com.produit = p.name), "\
                  "douane2 AS ( "\
                  "SELECT p.name as produit, coalesce(qtedeclaree,0) as qtedeclaree "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(d.qtedeclaree),0) as qtedeclaree "\
                  "FROM oms_douane d, product_template p "\
                  "WHERE d.iddecade = "+str(dec2)+" AND d.idproduit = p.id "\
                  "GROUP BY p.name) douane ON douane.produit = p.name), "\
                  "decade2 AS ( " \
                  "SELECT p.name as produit, s.qtesortie, d.qtedeclaree, d.qtedeclaree-s.qtesortie as ecart FROM product_template p "\
                  "LEFT JOIN sortie2 s "\
                  "ON s.produit = p.name "\
                  "LEFT JOIN douane2 d "\
                  "ON d.produit = p.name "\
                  "ORDER BY p.name ), "\
                  "sortie3 AS ( "\
                  "SELECT p.name as produit, coalesce(qtesortie,0) as qtesortie "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(c.quantite),0) as qtesortie "\
                  "FROM oms_facture_ligne l, oms_facture f, oms_commande c, product_template p "\
                  "WHERE l.idfacture = f.id "\
                  "AND l.idlcommande = c.idcom "\
                  "AND c.idproduit = p.id "\
                  "AND f.datesortie BETWEEN (SELECT debut FROM oms_decade WHERE id ="+str(dec3)+") AND (SELECT fin FROM oms_decade WHERE id ="+str(dec3)+") "\
                  "AND c.localite like '%ouaga%' GROUP BY p.name) com ON com.produit = p.name), "\
                  "douane3 AS ( "\
                  "SELECT p.name as produit, coalesce(qtedeclaree,0) as qtedeclaree "\
                  "FROM product_template p "\
                  "LEFT JOIN ( "\
                  "SELECT p.name as produit, coalesce(sum(d.qtedeclaree),0) as qtedeclaree "\
                  "FROM oms_douane d, product_template p "\
                  "WHERE d.iddecade = "+str(dec3)+" AND d.idproduit = p.id "\
                  "GROUP BY p.name) douane ON douane.produit = p.name), "\
                  "decade3 AS ( " \
                  "SELECT p.name as produit, s.qtesortie, d.qtedeclaree, d.qtedeclaree-s.qtesortie as ecart FROM product_template p "\
                  "LEFT JOIN sortie3 s "\
                  "ON s.produit = p.name "\
                  "LEFT JOIN douane3 d "\
                  "ON d.produit = p.name "\
                  "ORDER BY p.name ) "\
                  "(SELECT d1.produit, d1.qtesortie as qtesortie1, d1.qtedeclaree as qtedeclaree1, d1.ecart as ecart1, d2.qtesortie as qtesortie2, d2.qtedeclaree as qtedeclaree2, d2.ecart as ecart2, d3.qtesortie as qtesortie3, d3.qtedeclaree as qtedeclaree3, d3.ecart as ecart3 "\
                  "FROM decade1 d1 "\
                  "JOIN decade2 d2 "\
                  "ON d1.produit = d2.produit "\
                  "JOIN decade3 d3 "\
                  "ON d1.produit = d3.produit) "\
                  "UNION ALL "\
                  "(SELECT 'TOTAL', sum(d1.qtesortie), sum(d1.qtedeclaree), sum(d1.ecart), sum(d2.qtesortie), sum(d2.qtedeclaree), sum(d2.ecart), sum(d3.qtesortie), sum(d3.qtedeclaree), sum(d3.ecart) "\
                  "FROM decade1 d1 "\
                  "JOIN decade2 d2 "\
                  "ON d1.produit = d2.produit "\
                  "JOIN decade3 d3 "\
                  "ON d1.produit = d3.produit)"
                  
        if found == 0:
           raise osv.except_osv((''), ('Au moins une decade de ce mois est inexistant'))
        else:
            cr.execute(requete)
            sdmlines = cr.dictfetchall()
        return sdmlines

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        sdmlines = self._etat_sortiedouanemois(data['form']['mois'],data['form']['annee'])
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'sdmlines': sdmlines,
        }
        return self.env['report'].render('oms.report_sortiedouanemois', docargs)