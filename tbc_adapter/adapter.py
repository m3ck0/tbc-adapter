import os

import requests


class TBCAdapterException(Exception):
    pass


class TBCAdapterMeta(type):
    """
        meta class to ensure that inherited class implements 
        not implemented attributes. Also decorate api methods
        to automatically return marked outputs from response dict
    """

    def __new__(cls, name, bases, body):
        if not 'pem_paths' in body:
            raise TBCAdapterException("class must have pem_paths property, "
                                      "returning paths of pem key and cert")
        if not 'service_url' in body:
            raise TBCAdapterException("class must have pem_paths property, "
                                      "returning payment gateway service url")

        for k, v in body.items():
            if callable(v) and hasattr(v, "api_out"):
                body[k] = TBCAdapterMeta.api_method(v)

        return super().__new__(cls, name, bases, body)

    @staticmethod
    def api_method(method):
        def wrapper(*a, **kw):
            method(*a, **kw)
            get = a[0].response.get
            return a[0].response if not get("status") else \
                {k: get(k) for k in getattr(method, "api_out", ())}
        return wrapper


class TBCAdapter(metaclass=TBCAdapterMeta):
    client_ip = None  # issuer client ip address
    trans_id = None  # transaction id (existing / bank generated)
    response = None  # bank gateway response converted to dict

    def __init__(self, client_ip, trans_id=None):
        self.trans_id = trans_id
        self.client_ip = client_ip

    # GATEWAY API METHODS

    def get_transaction_id(self, amount, **kw):
        self._trans_related_common(amount, 'a', **kw)
    get_transaction_id.api_out = ("TRANSACTION_ID", )

    def get_transaction_status(self):
        self._request({
            'client_ip_addr': self.client_ip,
            'trans_id': self.trans_id,
            'command': 'c'
        })
    get_transaction_status.api_out = ("RESULT", "RESULT_CODE", "CARD_NUMBER")

    def end_business_day(self):
        self._request({'command': 'b'})
    end_business_day.api_out = ("RESULT", "RESULT_CODE")

    def get_preauthed_transaction_id(self, amount, **kw):
        self._trans_related_common(amount, 'a', **kw)
    get_preauthed_transaction_id.api_out = ("TRANSACTION_ID", )

    def commit_preauthed(self, amount, **kw):
        self._trans_related_common(amount, 't', **kw)
    commit_preauthed.api_out = ("RESULT", "RESULT_CODE", "CARD_NUMBER")

    def reverse_transaction(self):
        self._request({'command': 'r', 'trans_id': self.trans_id})
    reverse_transaction.api_out = ("RESULT", "RESULT_CODE")

    def refund_transaction(self, amount=None):
        """
            refund transaction api method, whole transaction amount will be
            refunded unless amount is provided   
            optional params:   
                amount [float] - transaction amount (<= whole trans amount)
        """
        self._request({
            'trans_id': self.trans_id,
            'amount': amount,  # find (Ctrl+F) 'note1'
            'command': 'k'
        })
    refund_transaction.api_out = ("RESULT", "RESULT_CODE")

    # INTERNAL UTIL METHODS

    def _trans_related_common(self, amount, cmd, **kw):
        """
            params:   
                amount [float] - transaction amount   
                cmd [str] - command code   
            optional params:   
                desc [ascii str] - transaction description   
                currecy [str] - transaction currency code (ISO 4217)   
                msg_type [str] - message type   
                language [str] - language code   
        """
        self._request({
            'desc': kw.pop('desc', 'not provided'),
            'currency': kw.pop('currency', '981'),
            'msg_type': kw.pop('msg_type', 'SMS'),
            'language': kw.pop('language', 'GE'),
            'client_ip_addr': self.client_ip,
            'trans_id': self.trans_id,  # find (Ctrl+F) 'note1'
            'amount': amount,
            'command': cmd
        })

    def _request(self, payload):
        """send POST request to self.service_url & store normalized response"""
        try:
            payload = {k: v for k, v in payload.items() if v is not None}
            response = requests.post(url=self.service_url, data=payload,
                                     cert=self.pem_paths, verify=False, timeout=3)

            if response.status_code == 200:
                self.response = self._raw_to_dict(response.text)
                self.response.update(status=True)
            else:
                raise requests.exceptions.HTTPError
        except requests.exceptions.ConnectTimeout:
            self.response = {"status": False, "desc": "timeout"}
        except requests.exceptions.SSLError:
            self.response = {"status": False, "desc": "ssl error"}
        except requests.exceptions.HTTPError:
            self.response = {"status": False, "desc": "http error"}
        except Exception:
            self.response = {"status": False, "desc": "general exception"}

    def _raw_to_dict(self, raw):
        """util method for converting gateway response to dict"""
        return dict(x.split(": ") for x in raw.split("\n") if x.strip() != "")

    # PROPS
    @property
    def pem_paths(self):
        """property for returning pem formatted certificate and private key"""
        raise NotImplementedError("pem_paths property must be implemented")

    @property
    def service_url(self):
        """property for returning bank gateway service url"""
        raise NotImplementedError("service_url property must be implemented")
