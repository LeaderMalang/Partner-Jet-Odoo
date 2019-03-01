# -*- coding: utf-8 -*-
{
    'name': 'Partner Jet Odoo Connector',
    'version': '1.0',
    'category': 'Other',
    'description': u"""
""",
    'author': 'YourCompany',
    'depends': ['base', 'sale_management', 'stock', 'delivery'],
    'data': [
            'security/ir.model.access.csv',
            'views/partner_jet_config_view.xml',
            'views/jet_category_view.xml',
            'views/product_view.xml',
            'views/wizard_import_script_view.xml',
            'views/partner_jet_order_view.xml',
    ],
    'application': False,
    'license': 'OPL-1',
}
