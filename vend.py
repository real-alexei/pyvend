import json
import urllib
import httplib


__version__ = "0.1.0"


class AccessToken(object):

    def __init__(self, token, token_type, expires, expires_in):
        self.token = token
        self.type = token_type
        self.expires = expires
        self.expires_in = expires_in


class Auth(object):
    """Authentication helper."""

    def __init__(self, app_id, app_secret, redirect_uri):
        self.id = app_id
        self.secret = app_secret
        self.redirect_uri = redirect_uri

    def get_auth_url(self):
        return 'https://secure.vendhq.com/connect?' + urllib.urlencode({
            'response_type': 'code',
            'client_id': self.id,
            'redirect_uri': self.redirect_uri
        })

    def request_token(self, code, domain_prefix):
        load = self._request('POST', domain_prefix, '/api/1.0/token', {
            'code': code,
            'client_id': self.id,
            'client_secret': self.secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        })
        return self._parse_token(load), load['refresh_token']

    def refresh_token(self, refresh_token, domain_prefix):
        return self._parse_token(self._request('POST', domain_prefix, '/api/1.0/token', {
            'refresh_token': refresh_token,
            'client_id': self.id,
            'client_secret': self.secret,
            'grant_type': 'refresh_token'
        }))

    @staticmethod
    def _parse_token(load):
        return AccessToken(load['access_token'],  load['token_type'], load['expires'], load['expires_in'])

    @staticmethod
    def _request(method, domain_prefix, path, params):
        c = httplib.HTTPSConnection(str(domain_prefix)+'.vendhq.com')
        try:
            c.request(method, path, urllib.urlencode(params), {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            })
            response = c.getresponse()
            return json.loads(response.read())
        finally:
            c.close()


class API(object):
    """Actual API wrapper which makes calls.

    Here is an example usage::

        api = API(access_token)
        api.customers(params={'email': 'aleks.selivanov@yahoo.com'}) # GET /api/customers?email=aleks.selivanov@yahoo.com
        api.supplier(post=data) # POST data to /api/supplier
        api.supplier(5, put=data) # PUT data to /api/supplier/5

    """

    def __init__(self, access_token, domain_prefix):
        self.token = access_token
        self.domain_prefix = domain_prefix
        self._base_headers = {
            'Accept': 'application/json',
            'Authorization': '%s %s' % (self.token.type, self.token.token)
        }

    def __getattr__(self, endpoint):
        def api_call(*args, **kwargs):
            path = '/api/'+endpoint+( '/'+'/'.join(args) if args else '' )
            payload = None
            if 'post' in kwargs:
                method = 'POST'
                payload = kwargs['post']
            elif 'put' in kwargs:
                method = 'PUT'
                payload = kwargs['put']
            elif 'delete' in kwargs:
                method = 'DELETE'
            else:
                method = 'GET'
                params = urllib.urlencode(kwargs)
                if params:
                    path += '?'+params

            print "API %s %s %s" % (method, path, pformat(payload))
            return self._request(method, path, payload)
        return api_call

    def _request(self, method, path, payload=None):
        c = httplib.HTTPSConnection(self.domain_prefix+'.vendhq.com')
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded' if method == 'GET' else 'application/json'}
            headers.update(self._base_headers)
            c.request(method, path, json.dumps(payload) if payload else None, headers)
            response = c.getresponse()
            response = json.loads(response.read())
            if 'error' in response:
                raise APIError(response['error'])
            return response
        finally:
            c.close()


class APIError(Exception):
    def __init__(self, message, details=None,  status=None):
        Exception.__init__(self, message)
        self.status = status
        self.details = details

    def __str__(self):
        if self.details:
            return "%s: %s" % (self.message, self.details)
        return self.message