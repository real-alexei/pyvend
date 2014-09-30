# pyvend&mdash;thin Vend API wrapper for Python

## Usage

Here are some examples.

    import os
    import vend


    # Authorization

    auth = vend.Auth(os.environ['VEND_CLIENT_ID'], os.environ['VEND_CLIENT_SECRET'], os.environ['VEND_REDIRECT_URI'])
    auth_url = auth.get_auth_url() # send retailer to this URL to authorize your client app
    ...
    access_token, refresh_token = auth.request_token(code, domain_prefix)


    # API

    api = API(access_token)
    api.customers(params={'email': 'aleks.selivanov@yahoo.com'}) # GET /api/customers?email=aleks.selivanov@yahoo.com
    api.supplier(post=data) # POST data to /api/supplier
    api.supplier(5, put=data) # PUT data to /api/supplier/5