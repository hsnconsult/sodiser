# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'oms',
    'version' : '1.1',
    'summary': 'Permet de gérer la vente de carburant',
    'sequence': 100,
    'description': """
Oil Management System
====================
    """,
    'category': 'Accounting',
    'website': 'http://www.hsnconsult.com',
    'depends': ['sale','base',],
    'data': [
        #'wizard/hydrovente_report_view.xml',
        #'views/report_sortiedouane.xml',
        #'views/report_sortiedouanetot.xml',
        #'views/report_venteclient.xml',
        #'views/report_venteproduit.xml',
        #'views/report_nonsorti.xml',
        #'views/report_sorti.xml',
        #'views/report_sortiedouanemois.xml',
        #'views/report_decade.xml',
        'views/oms_report.xml',
        'views/report_bel.xml',
        'views/report_bliv.xml',
        'views/report_facture.xml',
        'views/report_avoir.xml',
        'views/report_paye.xml',
        'views/oms_view.xml',
        #'views/oms_menuitem.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False
}
