# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_venteproduit(models.AbstractModel):
    _name = 'report.oms.report_venteproduit'

    def _etat_venteproduit(self,debut,fin):
        cr = self.env.cr
        requete = "(SELECT p.name as produit, sum(v.quantite) as quantite, sum(v.montant) as montant " \
                  "FROM oms_commande v, product_template p " \
                  "WHERE v.idproduit = p.id " \
                  "AND v.datebon BETWEEN '"+debut+"' AND '"+fin+"' " \
                  "GROUP BY p.name) " \
                  "UNION ALL " \
                  "(SELECT 'TOTAL',0,sum(montant) " \
                  "FROM oms_commande " \
                  "WHERE datebon BETWEEN '"+debut+"' AND '"+fin+"') " \
                  "ORDER BY produit "
        cr.execute(requete)
        vplines = cr.dictfetchall()
        return vplines
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        vplines = self._etat_venteproduit(data['form']['debut'],data['form']['fin'])
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'vplines': vplines,
        }
        return self.env['report'].render('oms.report_venteproduit', docargs)