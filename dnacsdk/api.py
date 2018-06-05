import json
import requests
import util as util
import exceptions
import datetime
import logging
import jwt

class Api(object):

    def __init__(self, **kwargs):
        """Create API object
        Usage::
            >>> import languages.python.scratch
            >>> api = dnacsdk.Api(ip="10.195.153.140", username='admin', password='Grapevine1')
        """

        self.ip = kwargs["ip"]  # Mandatory parameter
        self.username = kwargs["username"]  # Mandatory parameter
        self.password = kwargs["password"]
        self.token = None
        self.token_request_at = None
        self.options = kwargs
        self.endpoint = 'https://'+self.ip

    def get_token(self):
        """Generate new token by making a POST request
            1. By using client credentials if validate_token_hash finds
            token to be invalid.
        """
        path = "/api/system/v1/auth/token"
        payload={}

        authentication = (self.username, self.password)

    #   self.validate_token()
        if self.token is not None:
            return self.token
        else:
            self.token = self.http_call(util.join_url(self.endpoint, path), "POST",verify=False, data=payload, auth=authentication)

        return self.token

    def validate_token(self):
        """Checks if token has expired and if so resets token
        """
        if self.token_request_at and self.token is not None:
            current = datetime.datetime.now()
            expires_in = jwt.decode(self.token, 'secret', options=None)
            if current >= expires_in:
                self.token = None

    def headers(self):
        """Default HTTP headers
        """
        token = self.get_token()

        logging.info("Token is:"+str(token['Token']))

        return {
            "X-Auth-Token": token['Token'],
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def http_call(self, url, method, **kwargs):
        """Makes a http call. Logs response information.
        """
        logging.info('Request[%s]: %s' % (method, url))
        start_time = datetime.datetime.now()

        logging.info("Method:"+method);
        logging.info("URL:" + url);

        response = requests.request(method, url, **kwargs)

        duration = datetime.datetime.now() - start_time
        logging.info('Response[%d]: %s, Duration: %s.%ss.' % (
        response.status_code, response.reason, duration.seconds, duration.microseconds))

        return self.handle_response(response, response.content.decode('utf-8'))

    def handle_response(self, response, content):
        """Validate HTTP response
        """
        status = response.status_code
        if status in (301, 302, 303, 307):
            raise exceptions.Redirection(response, content)
        elif 200 <= status <= 299:
            return json.loads(content) if content else {}
        elif status == 400:
            raise exceptions.BadRequest(response, content)
        elif status == 401:
            raise exceptions.UnauthorizedAccess(response, content)
        elif status == 403:
            raise exceptions.ForbiddenAccess(response, content)
        elif status == 404:
            raise exceptions.ResourceNotFound(response, content)
        elif status == 405:
            raise exceptions.MethodNotAllowed(response, content)
        elif status == 409:
            raise exceptions.ResourceConflict(response, content)
        elif status == 410:
            raise exceptions.ResourceGone(response, content)
        elif status == 422:
            raise exceptions.ResourceInvalid(response, content)
        elif 401 <= status <= 499:
            raise exceptions.ClientError(response, content)
        elif 500 <= status <= 599:
            raise exceptions.ServerError(response, content)
        else:
            raise exceptions.ConnectionError(response, content, "Unknown response code: #{response.code}")

    def get(self, action, headers=None):
        """Make GET request
        Usage::
            >>> api.get("v1/payments/payment?count=1")
            >>> api.get("v1/payments/payment/PAY-1234")
        """
        http_headers = util.merge_dict(self.headers(), headers or {})

        return self.request(util.join_url(self.endpoint, action), 'GET', headers=http_headers or {})

    def post(self, action, params=None, headers=None):
        """Make POST request
        Usage::
            >>> api.post("v1/payments/payment", { 'indent': 'sale' })
            >>> api.post("v1/payments/payment/PAY-1234/execute", { 'payer_id': '1234' })
        """
        http_headers = util.merge_dict(self.headers(), headers or {})
        return self.request(util.join_url(self.endpoint, action), 'POST', body=params or {}, headers=http_headers or {})

    def put(self, action, params=None, headers=None):
        """Make PUT request
        Usage::
            >>> api.put("v1/invoicing/invoices/INV2-RUVR-ADWQ", { 'id': 'INV2-RUVR-ADWQ', 'status': 'DRAFT'})
        """
        return self.request(util.join_url(self.endpoint, action), 'PUT', body=params or {}, headers=headers or {})


    def delete(self, action, headers=None):
        """Make DELETE request
        """
        return self.request(util.join_url(self.endpoint, action), 'DELETE', headers=headers or {})

    def request(self, url, method, body=None, headers=None):
        """Make HTTP call, formats response and does error handling. Uses http_call method in API class.
        Usage::
            >>> api.request("https://api.sandbox.paypal.com/v1/payments/payment?count=10", "GET", {})
            >>> api.request("https://api.sandbox.paypal.com/v1/payments/payment", "POST", "{}", {} )
        """
        try:
            return self.http_call(url, method, data=json.dumps(body), verify=False,headers=headers)

        # Format Error message for bad request
        except exceptions.BadRequest as error:
            return {"error": json.loads(error.content)}

        # Handle Expired token
        except exceptions.UnauthorizedAccess as error:
            if self.token and self.username and self.password:
                self.token = None
                return self.request(url, method, body, headers)
            else:
                raise error


    __api__ = None

    # def default():
    #     """Returns default api object and if not present creates a new one
    #     By default points to developer sandbox
    #     """
    #     global __api__
    #     if __api__ is None:
    #         try:
    #             client_id = os.environ["PAYPAL_CLIENT_ID"]
    #             client_secret = os.environ["PAYPAL_CLIENT_SECRET"]
    #         except KeyError:
    #             raise exceptions.MissingConfig(
    #                 "Required PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET. Refer https://github.com/paypal/rest-api-sdk-python#configuration")
    #
    #         __api__ = Api(mode=os.environ.get("PAYPAL_MODE", "sandbox"), client_id=client_id,
    #                       client_secret=client_secret)
    #     return __api__

    def set_config(options=None, **config):
        """Create new default api object with given configuration
        """
        global __api__
        __api__ = Api(options or {}, **config)
        return __api__

    configure = set_config
