from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import Warning
import barcode
from  datetime import datetime
from odoo import http

def get_barcode_number_odoo(self, barcode_type):
    if barcode_type in ['EAN', 'GTIN']:
        barcode_code = barcode.ean.EuropeanArticleNumber13(str(self.id) + datetime.now().strftime("%S%M%H%d%m%y"))
    if barcode_type == 'ISBN-13':
        barcode_code = barcode.isxn.InternationalStandardBookNumber13('978' + str(self.id) + datetime.now().strftime("%S%M%H%d%m%y"))
    if barcode_type == 'ISBN-10':
        barcode_code = barcode.isxn.InternationalStandardBookNumber10(str(self.id) + datetime.now().strftime("%S%M%H%d%m%y"))
    else:
        return barcode_code.get_fullcode()


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_barcode_type = fields.Selection([('GTIN', 'GTIN'), ('EAN', 'EAN'),
        ('ISBN-10', 'ISBN-10'), ('ISBN-13', 'ISBN-13')], string="Barcode Type", default='EAN')
    jet_status = fields.Selection([('Uploaded', 'Uploaded'), ('Not Uploaded', 'Not Uploaded')], string="Status", default='Not Uploaded')
    product_jet_sku_id = fields.Char(string="Product SKU")

    brand = fields.Char(string="Brand")
    product_description = fields.Text(string="Product Description")
    manufacturer = fields.Char(string="Manufacturer")
    mfr_part_number = fields.Char(string="Part number")
    map_price = fields.Float(string="MAP Price")
    map_implementation = fields.Selection([('101', '101'), ('102', '102'), ('103', '103')], string="Map Implementation")
#     number_units_for_price_per_unit = fields.Integer(String="Price Per unit", default=1)
    shipping_weight_pounds = fields.Float(string="Shipping Weight Pounds")
    package_length_inches = fields.Float(string="Package Length Inches")
    package_width_inches = fields.Float(string="Package Width Inches")
    package_height_inches = fields.Float(string="Package Height Inches")
    display_length_inches = fields.Float(string="Display Length Inches")
    display_width_inches = fields.Float(string="Display Width Inches")
    display_height_inches = fields.Float(string="Display Height Inches")
    prop_65 = fields.Boolean(string="Prod 65")
    legal_disclaimer_description = fields.Char(String="Legal Disclaimer Description")
    country_of_origin = fields.Char(String="Country Of Origin")
    safety_warning = fields.Char(String="Safety Warning")
    product_tax_code = fields.Selection([('Toilet Paper', 'Toilet Paper'),
                                         ('Thermometers', 'Thermometers'),
                                         ('Sweatbands', 'Sweatbands'),
                                         ('SPF Suncare Products', 'SPF Suncare Products'),
                                         ('Sparkling Water', 'Sparkling Water'),
                                         ('Smoking Cessation', 'Smoking Cessation'),
                                         ('Shoe Insoles', 'Shoe Insoles'),
                                         ('Safety Clothing', 'Safety Clothing'),
                                         ('Pet Foods', 'Pet Foods'),
                                         ('Paper Products', 'Paper Products'),
                                         ('OTC Pet Meds', 'OTC Pet Meds'),
                                         ('OTC Medication', 'OTC Medication'),
                                         ('Oral Care Products', 'Oral Care Products'),
                                         ('Non-Motorized Boats', 'Non-Motorized Boats'),
                                         ('Non Taxable Product', 'Non Taxable Product'),
                                         ('Mobility Equipment', 'Mobility Equipment'),
                                         ('Medicated Personal Care Items', 'Medicated Personal Care Items'),
                                         ('Infant Clothing', 'Infant Clothing'),
                                         ('Helmets', 'Helmets'),
                                         ('Handkerchiefs', 'Handkerchiefs'),
                                         ('Generic Taxable Product', 'Generic Taxable Product'),
                                         ('General Grocery Items', 'General Grocery Items'),
                                         ('General Clothing', 'General Clothing'),
                                         ('Fluoride Toothpaste', 'Fluoride Toothpaste'),
                                         ('Feminine Hygiene Products', 'Feminine Hygiene Products'),
                                         ('Durable Medical Equipment', 'Durable Medical Equipment'),
                                         ('Drinks under 50 Percent Juice', 'Drinks under 50 Percent Juice'),
                                         ('Disposable Wipes', 'Disposable Wipes'),
                                         ('Disposable Infant Diapers', 'Disposable Infant Diapers'),
                                         ('Dietary Supplements', 'Dietary Supplements'),
                                         ('Diabetic Supplies', 'Diabetic Supplies'),
                                         ('Costumes', 'Costumes'),
                                         ('Contraceptives', 'Contraceptives'),
                                         ('Contact Lens Solution', 'Contact Lens Solution'),
                                         ('Carbonated Soft Drinks', 'Carbonated Soft Drinks'),
                                         ('Car Seats', 'Car Seats'),
                                         ('Candy with Flour', 'Candy with Flour'),
                                         ('Candy', 'Candy'),
                                         ('Breast Pumps', 'Breast Pumps'),
                                         ('Braces and Supports', 'Braces and Supports'),
                                         ('Bottled Water Plain', 'Bottled Water Plain'),
                                         ('Beverages with 51 to 99 Percent Juice', 'Beverages with 51 to 99 Percent Juice'),
                                         ('Bathing Suits', 'Bathing Suits'),
                                         ('Bandages and First Aid Kits', 'Bandages and First Aid Kits'),
                                         ('Baby Supplies', 'Baby Supplies'),
                                         ('Athletic Clothing', 'Athletic Clothing'),
                                         ('Adult Diapers', 'Adult Diapers')
                                         ], string="Product Tax Code")

    jet_attribute_ids = fields.Many2many('product.attribute', 'table_prod_jet_attribute_relation', string="Attribute")

    @api.multi
    def toggle_active(self):
        if self.jet_status == 'Uploaded' and self.product_jet_sku_id:
            partner_jet_config_obj = self.env['partner.jet.config']
            partner_jet_config_obj = partner_jet_config_obj.search([], order='id desc', limit=1)
            if not partner_jet_config_obj:
                raise Warning(_('Please make sure configuration first.'))
            partner_api = partner_jet_config_obj.do_connection()
            if partner_api:
                id_token = 'bearer' + ' ' + partner_api.get('id_token')
                headers = {'content-type': 'application/json', 'Authorization':id_token}
                product_archived_url = 'https://merchant-api.jet.com/api/merchant-skus/' + self.product_jet_sku_id +  '/status/archive'
                archived  = {"is_archived": self.active}
                r = requests.put(url=product_archived_url,data=json.dumps(archived),headers=headers)

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if res:
            if not vals.get('barcode') and vals.get('product_barcode_type'):
                bcode = get_barcode_number_odoo(res, vals.get('product_barcode_type'))
                res.write({'barcode': bcode})
        return res

    @api.multi
    def write(self, vals):
        for each in self:
            if vals.get('product_barcode_type'):
                bcode = get_barcode_number_odoo(each, vals.get('product_barcode_type'))
                vals.update({'barcode': bcode})
        return super(ProductProduct, self).write(vals)

    @api.multi
    def do_product_upload(self):
        if not self.barcode:
            raise Warning(_('Please Enter barcode number.'))

        product_image_path = '/web/image/product.product/%s/image' % self.id
        url = http.request.env['ir.config_parameter'].get_param('web.base.url') + product_image_path
        partner_jet_config_obj = self.env['partner.jet.config']
        partner_jet_config_obj = partner_jet_config_obj.search([], order='id desc', limit=1)
        if not partner_jet_config_obj:
            raise Warning(_('Please make sure configuration first.'))
        partner_api = partner_jet_config_obj.do_connection()
        if partner_api:
            try:
                attribute_ids = []
                product_url = "https://merchant-api.jet.com/api/merchant-skus/" + str(self.id) + self.default_code
                id_token = 'bearer' + ' ' + partner_api.get('id_token')
                headers = {'content-type': 'application/json', 'Authorization':id_token}
                for each_att_value_ids in self.attribute_value_ids:
                    attribute_ids.append({'attribute_id':each_att_value_ids.id, 'attribute_value':each_att_value_ids.name,
                                          'attribute_value_unit':each_att_value_ids.units})

                product = {"product_title": self.name, "jet_browse_node_id":int(float(self.categ_id.jet_categ_id)),
                           "standard_product_codes": [{"standard_product_code": self.barcode, "standard_product_code_type": self.product_barcode_type}],
                            "multipack_quantity": 1, "brand": self.brand if self.brand else self.name,
                            "main_image_url": url }
                if self.manufacturer:
                    product["manufacturer"] = self.manufacturer
                if self.mfr_part_number:
                    product['mfr_part_number'] = self.mfr_part_number
                if self.product_description:
                    product['product_description'] = self.product_description
                if self.shipping_weight_pounds:
                    product['shipping_weight_pounds'] = self.shipping_weight_pounds
                if attribute_ids:
                    product['attributes_node_specific'] = attribute_ids
                if self.package_length_inches:
                    product['package_length_inches'] = self.package_length_inches
                if self.package_width_inches:
                    product['package_width_inches'] = self.package_width_inches
                if self.package_height_inches:
                    product['package_height_inches'] = self.package_height_inches
                if self.display_length_inches:
                    product['display_length_inches'] = self.display_length_inches
                if self.display_width_inches:
                    product['display_width_inches'] = self.display_width_inches
                if self.display_height_inches:
                    product['display_height_inches'] = self.display_height_inches
                if self.prop_65:
                    product['prop_65'] = self.prop_65
                if self.legal_disclaimer_description:
                    product['legal_disclaimer_description'] = self.legal_disclaimer_description
                if self.country_of_origin:
                    product['country_of_origin'] = self.country_of_origin
                if self.safety_warning:
                    product['safety_warning'] = self.safety_warning
                if self.map_price:
                    product['map_price'] = self.map_price
                if self.map_implementation:
                    product['map_implementation'] = self.map_implementation
                if self.product_tax_code:
                    product['product_tax_code'] = self.product_tax_code

                r = requests.put(url=product_url, data=json.dumps(product), headers=headers)
                if r.status_code == 201:
                    self.write({'jet_status':'Uploaded', 'product_jet_sku_id':str(self.id) + self.default_code})
                if r.status_code not in [200, 201, 202]:
                    raise Warning(_(r.json()))
            except Exception as e:
                raise Warning(_(e))

    @api.multi
    def do_product_sync_price(self):
        if self.lst_price <= 0.00:
            raise Warning(_('Product price should be greater 0.'))
        partner_jet_config_obj = self.env['partner.jet.config']
        partner_jet_config_obj = partner_jet_config_obj.search([], order='id desc', limit=1)
        if not partner_jet_config_obj:
            raise Warning(_('Please make sure configuration first.'))
        partner_api = partner_jet_config_obj.do_connection()
        if partner_api:
            try:
                id_token = 'bearer' + ' ' + partner_api.get('id_token')
                headers = {'content-type': 'application/json', 'Authorization':id_token}
                price_upload_url = 'https://merchant-api.jet.com/api/merchant-skus/' + self.product_jet_sku_id + '/price'
                price_upload = {"price": self.lst_price}
                r = requests.put(url=price_upload_url, data=json.dumps(price_upload), headers=headers)
                if r.status_code not in [200, 201, 202]:
                    raise Warning(_(r.json()))
            except Exception as e:
                raise Warning(_(e))

    @api.multi
    def do_product_sync_inventory(self):
        partner_jet_config_obj = self.env['partner.jet.config']
        partner_jet_config_obj = partner_jet_config_obj.search([], order='id desc', limit=1)
        if not partner_jet_config_obj:
            raise Warning(_('Please make sure configuration first.'))
        qty_availability = self.with_context(location=partner_jet_config_obj.location_id.id, compute_child=False).qty_available
        if int(qty_availability) <= 0:
            raise Warning(_('Product %s has not enough quantity on %s location.') % (self.name, partner_jet_config_obj.location_id.name))
        partner_api = partner_jet_config_obj.do_connection()
        if partner_api:
            try:
                id_token = 'bearer' + ' ' + partner_api.get('id_token')
                headers = {'content-type': 'application/json', 'Authorization':id_token}
                inventory_upload = {"fulfillment_nodes": [{
                                        "fulfillment_node_id": partner_jet_config_obj.fulfillment_node_id,
                                        "quantity": int(qty_availability)}]
                                    }
                inventory_upload_url = 'https://merchant-api.jet.com/api/merchant-skus/' + self.product_jet_sku_id + '/inventory'
                r = requests.patch(url=inventory_upload_url, data=json.dumps(inventory_upload), headers=headers)
                if r.status_code not in [200, 201, 202]:
                    raise Warning(_(r.json()))
            except Exception as e:
                raise Warning(_(e))


class product_attribute(models.Model):
    _inherit = 'product.attribute'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('categ_id'):
            category_id = self.env['product.category'].browse(self._context.get('categ_id'))
            args.append(('id', 'in', [x.id  for x in category_id.attribute_ids]))
        return super(product_attribute, self).name_search(name, args, operator, 100000)


class product_attribute_value(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # for exceed the limit. default is 160
        return super(product_attribute_value, self).name_search(name, args, operator, 10000)


class product_category(models.Model):
    _inherit = 'product.category'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # for exceed the limit. default is 160
        return super(product_category, self).name_search(name, args, operator, 1000)

