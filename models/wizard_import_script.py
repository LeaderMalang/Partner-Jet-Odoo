from odoo import models, fields, api, _
from odoo.exceptions import Warning
import xlrd
import tempfile
import binascii

class product_category(models.Model):
    _inherit = 'product.category'

    jet_categ_id = fields.Char(string="Jet Category ID")
    categ_level = fields.Integer(string="Category Level")
    is_jet_categ = fields.Boolean(string="Is Jet Category")
    attribute_ids = fields.Many2many('product.attribute', 'table_product_categ_attr_relation', 'categ_id', 'att_id', string="Attributes")


class product_attribute(models.Model):
    _inherit = 'product.attribute'

    jet_attribute_id = fields.Char(string="Jet Attribute ID")
    is_jet_attribute = fields.Boolean(string="Is Jet Attribute")
    description = fields.Text(string="Description")
    free_text = fields.Selection([('No', 'No'), ('Yes', 'Yes')], string="Free Text")
    facet_filter = fields.Selection([('No', 'No'), ('Yes', 'Yes')], string="Facet Filter")
    category_ids = fields.Many2many('product.category', 'table_product_categ_attr_relation', 'att_id', 'categ_id', string="Category")


class product_attribute_value(models.Model):
    _inherit = 'product.attribute.value'

    units = fields.Char(string="Units")
    is_jet_value = fields.Boolean(string="Is Jet Attribute Value")


class wizard_import_script(models.TransientModel):
    _name = 'wizard.import.script'

    file = fields.Binary('File')

    @api.multi
    def import_attribute_value(self):
        if not self.file:
            raise Warning(_('please upload .xlsx file.'))
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(3)
        value_obj = self.env['product.attribute.value'].with_context({'default_is_jet_value': True})
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:row.value, sheet.row(row_no)))
                if line:
                    attribute_id = self.env['product.attribute'].search([('jet_attribute_id', '=', str(int(line[0])).strip())], limit=1)
                    if attribute_id:
                        value_id = value_obj.search([('name', '=', str(line[1]).strip()),
                                                     ('attribute_id', '=', attribute_id.id)], limit=1)
                        if not value_id:
                            value_obj.create({'attribute_id': attribute_id.id,
                                              'name': str(line[1]).strip(),
                                              'units': line[2].strip()})


    @api.multi
    def import_product_category(self):
        if not self.file:
            raise Warning(_('please upload .xlsx file.'))
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(1)
        categ_obj = self.env['product.category'].with_context({'default_is_jet_categ': True})
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:row.value, sheet.row(row_no)))
                if line:
                    # level 0
                    l0_cid = categ_obj.search([('jet_categ_id', '=', str(int(line[0])).strip())], limit=1)
                    if not l0_cid:
                        l0_cid = categ_obj.create({'name': line[1].strip(),
                                                   'jet_categ_id': str(int(line[0])).strip(),
                                                   'categ_level': 0})
                    # level 1
                    l1_cid = categ_obj.search([('jet_categ_id', '=', str(int(line[2])).strip())], limit=1)
                    if not l1_cid:
                        l1_cid = categ_obj.create({'name': line[3].strip(),
                                                   'jet_categ_id': str(int(line[2])).strip(),
                                                   'categ_level': 1,
                                                   'parent_id': l0_cid.id})
                    # level 2
                    l2_cid = categ_obj.search([('jet_categ_id', '=', str(int(line[4])).strip())], limit=1)
                    if not l2_cid:
                        l2_cid = categ_obj.create({'name': line[5].strip(),
                                                   'jet_categ_id': str(int(line[4])).strip(),
                                                   'categ_level': 2,
                                                   'parent_id': l1_cid.id})

    @api.multi
    def import_attribute(self):
        if not self.file:
            raise Warning(_('please upload .xlsx file.'))
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(2)
        attobj = self.env['product.attribute'].with_context({'default_is_jet_attribute': True})
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:row.value, sheet.row(row_no)))
                if line:
                    aid = attobj.search([('jet_attribute_id', '=', str(int(line[0])).strip())], limit=1)
                    if not aid:
                        attobj.create({'jet_attribute_id': str(int(line[0])).strip(),
                                       'description': line[1].strip(),
                                       'name': line[2].strip(),
                                       'free_text': line[3].strip(),
                                       'create_variant': True if line[4].strip() == 'Yes' else False,
                                       'facet_filter': line[5].strip()})


    @api.multi
    def map_category_attribute(self):
        if not self.file:
            raise Warning(_('please upload .xlsx file.'))
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(4)
        attobj = self.env['product.attribute']
        categobj = self.env['product.category']
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:row.value, sheet.row(row_no)))
                if line:
                    categ_id = categobj.search([('jet_categ_id', '=', str(int(line[0])).strip())], limit=1)
                    att_id = attobj.search([('jet_attribute_id', '=', str(int(line[1])).strip())], limit=1)
                    if categ_id and att_id:
                        categ_id.attribute_ids += att_id
