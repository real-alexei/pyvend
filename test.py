import unittest
import os
import urllib
import urllib2
import httplib
import urlparse
from HTMLParser import HTMLParser
import vend


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.auth = vend.Auth(os.environ['VEND_CLIENT_ID'], os.environ['VEND_CLIENT_SECRET'], os.environ['VEND_REDIRECT_URI'])

    def test_api(self):
        auth_url = self.auth.get_auth_url() 

        # Fill in form
        auth_page = urllib2.urlopen(auth_url)
        assert auth_page.code == 200
        vend_cookie = dict(auth_page.headers)['set-cookie'].split(';')[0]
        parser = AuthFormParser()
        parser.feed(auth_page.read())
        parser.data.update({
            'signin[retailer_domain_prefix]': os.environ['STORE_ADDRESS'],
            'signin[username]': os.environ['STORE_USERNAME'],
            'signin[password]': os.environ['STORE_PASSWORD'],
            'authorize': 1
        })

        # POST form
        c = httplib.HTTPSConnection('secure.vendhq.com')
        c.request('POST', '/connect', urllib.urlencode(parser.data), {
            'Cookie': vend_cookie,
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        # Extract ``code`` and ``domain_prefix`` from the redirect target URL
        redirect = c.getresponse()
        assert redirect.status == 302
        url = dict(redirect.getheaders())['location']
        qs = urlparse.urlparse(url).query
        params = urlparse.parse_qs(qs)
        code = params['code'][0]
        domain_prefix = params['domain_prefix'][0]
        assert domain_prefix == os.environ['STORE_ADDRESS']
                
        # Request auth token pair: access & refresh
        token = self.auth.request_token(code, domain_prefix)
        self._assert_token(token, refresh_token_required=True)

        # Refresh access token
        token = self.auth.refresh_token(token, domain_prefix)
        self._assert_token(token, refresh_token_required=False)

        api = vend.API(token, domain_prefix)

        # Wrong endpoint name will raise APIError
        try:
            api.blah()
        except vend.APIError, e:
            assert e.status == 404
            
        # Invalid input
        response = api.products(post={"invalid": "data"})
        assert response['status'] == 'error'
        assert 'error' in response
        assert 'details' in response

        # Create a product (POST)
        response = api.products(post={
            'source_id': 'magento-123',
            'source_variant_id': 'magento-variant-1-123',
            'handle': 'iPad2',
            'type': 'General',
            'tags': 'Apple, iPad',
            'name': 'iPad 2',
            'description': 'Second generation iPad',
            'sku': 'ipad2123',
            'variant_option_one_name': 'Memory',
            'variant_option_one_value': '64gb',
            'variant_option_two_name': 'Wireless',
            'variant_option_two_value': 'WiFi',
            'variant_option_three_name': None,
            'variant_option_three_value': None,
            'supply_price': '800.95',
            'retail_price': '1400.95',
            'brand_name': 'Apple',
            'supplier_name': 'Apple',
            'supplier_code': 'aplipad264',
            'inventory': [
            {
                'outlet_name': 'our retail store',
                'count': 22,
                'reorder_point': 33,
                'restock_level': 11
            }]
        })
        assert 'product' in response
        product = response['product']
        assert 'id' in product
        assert api.products(product['id'], delete=True)['status'] == 'success'

        # Filter (GET)
        customers = api.customers(email='there is no user with email like this')
        assert 'customers' in customers
        assert [] == customers['customers']

    def _assert_token(self, token, refresh_token_required):
        assert isinstance(token, vend.Token)
        assert token.access_token
        assert token.type == 'Bearer'
        assert token.expires
        assert token.expires_in
        if refresh_token_required:
            assert token.refresh_token


class AuthFormParser(HTMLParser):

    def __init__(self): 
        self.form = False
        self.data = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'form' and ('action', '/connect') in attrs:
            self.form = True
        if self.form and tag in ('input', 'select', 'textarea', 'button'):
            attrs = dict(attrs)
            if 'name' in attrs and 'value' in attrs:
                self.data[attrs.get('name')] = attrs.get('value')

    def handle_endtag(self, tag):
        if tag == 'form' and hasattr(self, 'form'):
            self.form = False


if __name__ == '__main__':
    unittest.main()