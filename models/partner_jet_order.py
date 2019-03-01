from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import Warning


class partner_jet_order(models.Model):
    _name = 'partner.jet.order'

    
    alt_order_id = fields.Char(string="Alt Order ID")
    status = fields.Selection([('created', 'Created'), ('ready', 'Ready'), ('acknowledged', 'Acknowledged'),
                               ('inprogress', 'inprogress'), ('complete', 'complete')], string="Status")
    merchant_order_id = fields.Char(string="Merchant Order ID")
    reference_order_id = fields.Char(string="Reference Order ID")
    has_shipments = fields.Boolean(string="Has Shipments")
    hash_email = fields.Char(string="Hash Email")
    
    jet_request_directed_cancel = fields.Boolean(string="Jet Request Direct Cancel")
    order_placed_date = fields.Datetime("Order Place Date")
    fulfillment_node = fields.Char(string="Fulfillment Note")
    customer_reference_order_id = fields.Char(string="Customer Reference Order ID")
    
    order_transmission_date = fields.Datetime("Order Transmission Date")
    
    item_shipping_cost = fields.Float(String="Item Shipping Cost")
    item_shipping_tax = fields.Float(String="Item Shipping Tax")
    base_price = fields.Float(string="Base Price")
    item_tax = fields.Float(string="Item Tax")
    partner_jet_lines = fields.One2many('partner.jet.order.lines','jet_order_id',string="Lines")


class partner_jet_order_lines(models.Model):
    _name = 'partner.jet.order.lines'

    jet_order_id = fields.Many2one('partner.jet.order',string="Jet Order")
    request_order_quantity = fields.Integer(string="Order Quantity")
    url = fields.Char(string="Url")
    order_cancel_qty = fields.Integer(string="Cancel Quantity")
    merchant_sku = fields.Char(string="Merchant SKU")
    item_tax_code = fields.Char(string="Item Tax Code")
    product_title = fields.Char(string="Product Title")
    order_item_id = fields.Char(string="Order Item ID")

