# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_venteclient(models.AbstractModel):
    _name = 'report.oms.report_venteclient'

    def _etat_venteclient(self,debut,fin):
        cr = self.env.cr
        requete = "(SELECT c.name, c.name AS client, p.name as produit, sum(v.quantite) as quantite, sum(v.montant) as montant " \
                  "FROM oms_commande v, res_partner c, product_template p " \
                  "WHERE v.idproduit = p.id " \
                  "AND v.idclient = c.id " \
                  "AND v.datebon BETWEEN '"+debut+"' AND '"+fin+"' " \
                  "GROUP BY c.name, client, p.name) " \
                  "UNION ALL " \
                  "(SELECT c.name||' TOTAL', 'CA de '||c.name, '', 0, sum(v.montant) " \
                  "FROM oms_commande v, res_partner c " \
                  "WHERE v.idclient = c.id " \
                  "AND v.datebon BETWEEN '"+debut+"' AND '"+fin+"' " \
                  "GROUP BY c.name, c.name) " \
                  "UNION ALL " \
                  "(SELECT 'ZTOTAL GENERAL', 'TOTAL GENERAL', '',0,sum(montant) " \
                  "FROM oms_commande " \
                  "WHERE datebon BETWEEN '"+debut+"' AND '"+fin+"') " \
                  "ORDER BY name "
        cr.execute(requete)
        vclines = cr.dictfetchall()
        return vclines
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        vclines = self._etat_venteclient(data['form']['debut'],data['form']['fin'])
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'vclines': vclines,
        }
        return self.env['report'].render('oms.report_venteclient', docargs)