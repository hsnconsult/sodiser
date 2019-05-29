# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_decade(models.AbstractModel):
    _name = 'report.oms.report_decade'

    def _etat_decade(self):
        cr = self.env.cr
        requete = "SELECT d.name as decade, p.name as produit, dn.qtedeclaree, dn.qteliquidee, dn.montant " \
                  "FROM oms_decade d, product_template p, oms_douane dn " \
                  "WHERE dn.iddecade = d.id " \
                  "AND dn.idproduit = p.id " \
                  "ORDER BY d.debut, p.name"
        cr.execute(requete)
        dlines = cr.dictfetchall()
        return dlines
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        dlines = self._etat_decade()
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'dlines': dlines,
        }
        return self.env['report'].render('oms.report_decade', docargs)