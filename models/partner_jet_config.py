from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import Warning


class partner_jet_config(models.Model):
    _name = 'partner.jet.config'

    url = fields.Char(string="URL")
    user = fields.Char(string="User")
    secret_key = fields.Char(string="Secret")
    merchant = fields.Char(string="Merchant")
    id_token = fields.Char(string="Token")
    token_type = fields.Text(string="Token Type")
    expires_on = fields.Char(string="Expire")
    fulfillment_node_id = fields.Char(string="Fulfillment Note")
    location_id = fields.Many2one('stock.location', string="Location")

    @api.model
    def default_get(self, fieldlist):
        res = super(partner_jet_config, self).default_get(fieldlist)
        config_id = self.search([], limit=1, order='id desc')
        if config_id:
            res.update({'url':config_id.url,
                        'user':config_id.user,
                        'secret_key':config_id.secret_key,
                        'merchant':config_id.merchant,
                        'id_token':config_id.id_token,
                        'token_type':config_id.token_type,
                        'expires_on':config_id.expires_on,
                        'fulfillment_node_id':config_id.fulfillment_node_id,
                        'location_id':config_id.location_id.id,
                        })
        return res

    @api.multi
    def do_connection(self):
        url = self.url
        headers = {'content-type': 'application/json'}
        payload = {"user":self.user, "pass":self.secret_key}
        r = requests.post(url=url, data=json.dumps(payload))
        json_data = r.json()
        if r.status_code != 200:
            raise Warning(_(json_data.get('Message')))
        elif r.status_code == 200:
            self.token_type = json_data.get('token_type')
            self.id_token = json_data.get('id_token')
            self.expires_on = json_data.get('expires_on')
        print( "====get_connect : ",self)
        return json_data

    @api.model
    def cron_do_connection(self):
        recid = self.search([], limit=1, order="id desc")
        if recid:
            return recid.do_connection()
