# -*- coding: utf-8 -*-
{
    "name": "Extension for vynex intercompany",
    "version": "18.0.0.0.0",
    'license': 'OPL-1',
    'summary': 'Extension for vynex intercompany',
    "description": """
        This module is an extension for the intercompany module. It adds a customer number to the invoice and purchase order.
        """,
    "category": 'base',
    'author': "CLuedoo",
    'website': "https://cluedoo.com",
    'support': 'support@cluedoo.com',
    "depends": [
        "purchase",
        "sale_purchase_inter_company_rules",
        "sale_management",
        "stock",
    ],
    "data": [
        "views/purchase_views.xml",
        "views/sale_views.xml",
        "views/stock_views.xml",
        "views/account_move_views.xml",
    ],
}
