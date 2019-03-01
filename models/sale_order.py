from odoo import models, fields, api, _
from odoo.exceptions import Warning
import requests
import json


class sale_order(models.Model):
    _inherit = 'sale.order'

    alt_order_id = fields.Char(string="Alt Order")
    status = fields.Selection([('created', 'Created'), ('ready', 'Ready'), ('acknowledged', 'Acknowledged'),
                               ('inprogress', 'inprogress'), ('complete', 'complete')], string="Jet Order Status")
    merchant_order_id = fields.Char(string="Merchant Order")
    reference_order_id = fields.Char(string="Reference Order")
    has_shipments = fields.Boolean(string="Has Shipments")
    hash_email = fields.Char(string="Hash Email")
    
    jet_request_directed_cancel = fields.Boolean(string="Jet Request Direct Cancel")
    order_placed_date = fields.Datetime("Order Place Date")
    fulfillment_node = fields.Char(string="Fulfillment Note")
    customer_reference_order_id = fields.Char(string="Customer Reference Order")
    
    order_transmission_date = fields.Datetime("Order Transmission Date")
    is_jet_order = fields.Boolean(string="Jet Sale Order")
#     item_shipping_cost = fields.Float(String="Item Shipping Cost")
#     item_shipping_tax = fields.Float(String="Item Shipping Tax")
#     base_price = fields.Float(string="Base Price")
#     item_tax = fields.Float(string="Item Tax")
#     partner_jet_lines = fields.One2many('partner.jet.order.lines','jet_order_id',string="Lines")
    acknowledgement_status = fields.Selection([('rejected - other', 'Rejected Other'),
                                               ('rejected - fraud', 'Rejected Fraud'),
                                               ('rejected - item level error', 'Rejected Item Level Error'),
                                               ('rejected - ship from location not available', 'Rejected Ship From Location Not Available'),
                                               ('rejected - shipping method not supported', 'Rejected Shipping Method Not Supported'),
                                               ('rejected - unfulfillable address', 'Rejected Unfulfillable Address'),
                                               ('accepted', 'accepted')
                                               ], compute='check_line_ack_status', string="Acknowledgement Status")

    @api.multi
    @api.depends('order_line')
    def check_line_ack_status(self):
        if all(line.order_item_acknowledgement_status == 'fulfillable' for line in self.order_line):
            self.update({'acknowledgement_status':'accepted'})

    @api.multi
    def action_confirm(self):
        if self.is_jet_order:
            partner_jet_config_obj = self.env['partner.jet.config']
            partner_jet_config_obj = partner_jet_config_obj.search([], order='id desc', limit=1)
            acknowledgement_status = {}
            order_items = []
            if partner_jet_config_obj:
                for each_line in self.order_line:
                    qty_available = each_line.product_id.with_context(location=partner_jet_config_obj.location_id.id, compute_child=False).qty_available
                    if qty_available > 0:
                        each_line.order_item_acknowledgement_status = 'fulfillable'
                    else:
                        each_line.order_item_acknowledgement_status = 'nonfulfillable - no inventory'
                    order_items.append({'order_item_acknowledgement_status':each_line.order_item_acknowledgement_status,
                                        'order_item_id':each_line.order_item_id})
                acknowledgement_status.update({'acknowledgement_status':self.acknowledgement_status,
                                               'alt_order_id':self.alt_order_id,
                                               'order_items':order_items})
                print ("\n\n --123---acknowledgement_status---", acknowledgement_status)
                try:
                    id_token = 'bearer' + ' ' + partner_jet_config_obj.id_token
                    headers = {'content-type': 'application/json', 'Authorization':id_token}
                    acknowledge_url = 'https://merchant-api.jet.com/api/orders/' + self.merchant_order_id + '/acknowledge'
                    r = requests.put(url=acknowledge_url, data=json.dumps(acknowledgement_status), headers=headers)
                    print ("\n\n --acknowledge uploaded----", r)
#                     if r.status_code not in [200, 201, 202]:
#                         raise Warning(_(r.json()))
                except Exception as e:
                    raise Warning(_(e))
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
            return True


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    url = fields.Char(string="URL")
    order_item_id = fields.Char(string="Order Item ID")
    item_tax_code = fields.Char(string="Item Tax Code")
    order_item_acknowledgement_status = fields.Selection([('nonfulfillable - invalid merchant SKU', 'Nonfulfillable - Invalid merchant SKU'),
                                                          ('nonfulfillable - no inventory', 'Nonfulfillable - No Inventory'),
                                                          ('fulfillable', 'Fulfillable')
                                                          ], string="Acknowledgement Status")

