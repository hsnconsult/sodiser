# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_nonsorti(models.AbstractModel):
    _name = 'report.oms.report_nonsorti'

    def _etat_nonsorti(self,debut,fin):
        cr = self.env.cr
        requete = "(SELECT v.numbon, to_char(v.datebon,'DD-MM-YYY') as datebon, c.name as client, p.name as produit, v.quantite, v.montant " \
                  "FROM oms_commande v, res_partner c, product_template p " \
                  "WHERE v.idproduit = p.id " \
                  "AND v.idclient = c.id " \
                  "AND v.factureh=False " \
                  "AND v.datebon BETWEEN '"+debut+"' AND '"+fin+"' " \
                  "ORDER BY datebon) " \
                  "UNION ALL " \
                  "(SELECT 'TOTAL','','','',0,sum(montant) " \
                  "FROM oms_commande " \
                  "WHERE datebon BETWEEN '"+debut+"' AND '"+fin+"' " \
                  "AND factureh=False) "
        cr.execute(requete)
        nslines = cr.dictfetchall()
        return nslines
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        nslines = self._etat_nonsorti(data['form']['debut'],data['form']['fin'])
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'nslines': nslines,
        }
        return self.env['report'].render('oms.report_nonsorti', docargs)