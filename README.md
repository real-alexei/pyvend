# pyvend is a thin Vend API wrapper for Python

## Usage

Here are some examples.

    import os
    import vend


    # Authorization

    auth = vend.Auth(os.environ['VEND_CLIENT_ID'], os.environ['VEND_CLIENT_SECRET'], os.environ['VEND_REDIRECT_URI'])
    auth_url = auth.get_auth_url() # send retailer to this URL to authorize your client app
    ...
    token = auth.request_token(code, domain_prefix)


    # API

    api = API(token)
    api.customers(params={'email': 'aleks.selivanov@yahoo.com'}) # GET /api/customers?email=aleks.selivanov@yahoo.com
    api.supplier(post=data) # POST data to /api/supplier
    api.supplier(5, put=data) # PUT data to /api/supplier/5

    # Handle errors
    try:
        api.blah()
    except vend.APIError, e:
        e.status # 404
        str(e) # {'error': 'Endpoint not found'}

    # Note that invalid input does not raise APIError and must be handled as normal response
    response = api.products(post={"invalid": "data"})
    # {
    #   'details': 'Missing handle',
    #   'error': 'Could not Add or Update',
    #   'status': 'error'
    # }