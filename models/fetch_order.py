from odoo import models, fields, api, _
from odoo.exceptions import Warning
import requests
import json


class fetch_jet_order(models.TransientModel):
    _name = 'fetch.jet.order'

    @api.multi
    def fetch(self):
#         partner_jet_order_obj = self.env['partner.jet.order']
        partner_jet_config_obj = self.env['partner.jet.config']
        sale_order_obj = self.env['sale.order']
        respart_obj = self.env['res.partner']
        partner_jet_config_obj = partner_jet_config_obj.search([], order='id desc', limit=1)
        if not partner_jet_config_obj:
            raise Warning(_('Please make sure configuration first.'))
        partner_api = partner_jet_config_obj.read()[0] or {}
        if partner_api:
            try:
                order_url = "https://merchant-api.jet.com/api/orders/ready?&fulfillment_node=" + partner_jet_config_obj.fulfillment_node_id
                id_token = 'bearer' + ' ' + partner_api.get('id_token')
                headers = {'content-type': 'application/json', 'Authorization':id_token}
                r = requests.get(url=order_url, headers=headers)
                if r.status_code != 200:
                    partner_api = partner_jet_config_obj.do_connection()
                    id_token = 'bearer' + ' ' + partner_api.get('id_token')
                    headers = {'content-type': 'application/json', 'Authorization':id_token}
                    r = requests.get(url=order_url, headers=headers)
                if r.status_code == 200:
                    for each_order in r.json().get('order_urls'):
                        order_detail_url = 'https://merchant-api.jet.com/api' + each_order
                        order_detail_req = requests.get(url=order_detail_url, headers=headers)
                        json_data = order_detail_req.json()
                        print ("\n\n --json_data---", json_data)

                        sale_id = sale_order_obj.search([('merchant_order_id', '=', json_data.get('merchant_order_id'))], limit=1)
                        if not sale_id:
                            sovals = {'order_placed_date':json_data.get('order_placed_date'),
                                      'status':json_data.get('status'),
                                      'merchant_order_id':json_data.get('merchant_order_id'),
                                      'reference_order_id':json_data.get('reference_order_id'),
                                      'hash_email':json_data.get('hash_email'),
                                      'customer_reference_order_id': json_data.get('customer_reference_order_id'),
                                      'fulfillment_node': json_data.get('fulfillment_node'),
                                      'has_shipments': json_data.get('has_shipments'),
                                      'jet_request_directed_cancel': json_data.get('jet_request_directed_cancel'),
                                      'alt_order_id': json_data.get('alt_order_id'),
                                      'is_jet_order': True
                                      }
                            partner_id = respart_obj.search([('name', '=', json_data.get('buyer').get('name')),
                                                             ('phone', '=', json_data.get('buyer').get('phone_number'))], limit=1)
                            if not partner_id:
                                partner_id = respart_obj.create({'name': json_data.get('buyer').get('name'),
                                                                 'phone': json_data.get('buyer').get('phone_number'),
                                                    })
                            sovals.update({'partner_id': partner_id.id or False})
                            name = partner_id.name
                            phone = partner_id.phone
                            if partner_id.name != json_data.get('shipping_to').get('recipient').get('name'):
                                name = json_data.get('shipping_to').get('recipient').get('name')
                                phone = json_data.get('shipping_to').get('recipient').get('phone_number')
                            partner_id.write({'child_ids': [(0, 0, {'street': json_data.get('shipping_to').get('address').get('address1') or "",
                                                                    'street2': json_data.get('shipping_to').get('address').get('address2') or "",
                                                                    'city': json_data.get('shipping_to').get('address').get('city') or "",
#                                                                             'state': json_data.get('shipping_to').get('address').get('state') or "",
                                                                    'zip': json_data.get('shipping_to').get('address').get('zip_code') or "",
#                                                                     'name': name,
#                                                                     'phone': phone,
                                                                    'type': 'delivery',
                                                                    'parent_id': partner_id.id}
                                                                 )]})
                            ship_part_id = partner_id.child_ids.filtered(lambda l: l.type == 'delivery' and l.name == name and l.phone == phone)
                            if ship_part_id:
                                sovals.update({'partner_shipping_id': ship_part_id[:-1].id})
                            # carrier
                            carrier_id = self.env['delivery.carrier'].search([('delivery_type', 'ilike', json_data.get('order_detail').get('request_shipping_carrier'))], limit=1)
                            if carrier_id:
                                sovals.update({'carrier_id': carrier_id.id})
                            orderlines = []
                            for line in json_data.get('order_items'):
                                prod_id = self.env['product.product'].search([('product_jet_sku_id', '=', line.get('merchant_sku'))], limit=1)
                                print ("\n\n --prod_id---", prod_id)
                                if prod_id:
                                    orderlines.append((0, 0, {'product_id': prod_id.id,
                                                        'name': line.get('product_title', prod_id.name),
                                                        'product_uom_qty': line.get('request_order_quantity', 0.0),
                                                        'price_unit': line.get('item_price').get('base_price'),
                                                        'url': line.get('url'),
                                                        'order_item_id': line.get('order_item_id'),
                                                        'item_tax_code': line.get('item_tax_code')}))
                            sovals.update({'order_line': orderlines})
                            sale_order_obj.create(sovals)
            except Exception as e:
                raise Warning(_(e))



