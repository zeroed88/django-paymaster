import requests

from uuid import uuid4
from hashlib import sha1
from base64 import b64encode
from typing import Dict


class PaymasterClientResponse(Dict):
    success: bool = False
    error: str = ""
    data: dict = {}

    def __init__(self, *args, **kwargs):
        self.success = kwargs.get("ErrorCode") == 0
        self.error = kwargs.get("Message") or ""
        self.data = kwargs.get("Response") or {}
        super().__init__(*args, **kwargs)


class PaymasterClient:
    _host = "https://paymaster.ru/api/v1/"
    _login = ""
    _password = ""
    _account_id = ""

    def __init__(self, account_id: str, login: str, password: str, host: str = None):
        self._account_id = account_id
        self._login = login
        self._password = password
        self._host = host or self._host

    def _get_nonce_param(self) -> str:
        return uuid4().hex

    def _get_hash(self, hash_params: str, data: dict = {}) -> str:
        hash_params_list = hash_params.split(";")
        hash_list = []

        for param in hash_params_list:
            if param == "password":
                hash_list.append(self._password)
            else:
                hash_list.append(str(data.get(param) or ""))

        hash_str = ";".join(hash_list)
        sha1_str = sha1(hash_str.encode("UTF-8"))
        return b64encode(sha1_str.digest()).decode("UTF-8")

    def _extend_params(self, hash_params: str, params: dict = {}) -> dict:
        params["login"] = self._login
        params["nonce"] = self._get_nonce_param()
        params["hash"] = self._get_hash(hash_params, params)
        return params

    def _request_get(self, method: str, params: dict = {}):
        return requests.get(f"{self._host}{method}", params=params)

    def list_payments_filter(
        self,
        site_alias: str,
        period_from: str = None,
        period_to: str = None,
        invoice_id: str = None,
        state: str = None,
    ) -> PaymasterClientResponse:
        params = self._extend_params(
            "login;password;nonce;accountID;siteAlias;periodFrom;periodTo;invoiceID;state",
            {
                "accountID": self._account_id,
                "siteAlias": site_alias,
                "periodFrom": period_from,
                "periodTo": period_to,
                "invoiceID": invoice_id,
                "state": state,
            },
        )
        response = self._request_get("listPaymentsFilter", params=params)
        return PaymasterClientResponse(**response.json())
