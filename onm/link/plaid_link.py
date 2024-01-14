
from plaid.api.plaid_api import PlaidApi
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from .link import Link
from .. import webserver


class PlaidLink(Link):

    def __init__(self, plaid_api : PlaidApi):
        self._plaid_api = plaid_api

    def get_access_token(self):
        link_token = self._get_link_token()
        public_token = self._get_public_token(link_token)
        access_token = self._exchange_public_token(public_token)
        return access_token

    def update_link(self, access_token: str):
        link_token = self._get_link_token(access_token)
        webserver.serve(
            clientName="onm",
            pageTitle="Update Account Credentials",
            type="update",
            token=link_token
        )

    def _get_link_token(self, access_token: str = None) -> str:
        data = {
            'user': {
                'client_user_id': 'onm',
            },
            'client_name': 'onm',
            'country_codes': [CountryCode('US')],
            'language': 'en',
        }
        if access_token:
            data['access_token'] = access_token
        else:
            data['products'] = [Products('transactions')]
        req = LinkTokenCreateRequest(**data)
        res = self._plaid_api.link_token_create(req)
        return res.link_token

    def _get_public_token(self, link_token: str = None) -> str:
        plaid_response = webserver.serve(
            clientName="onm",
            pageTitle="Link Account Credentials",
            type="link",
            token=link_token
        )
        return plaid_response['public_token']

    def _exchange_public_token(self, public_token: str) -> str:
        req = ItemPublicTokenExchangeRequest(public_token)
        res = self._plaid_api.item_public_token_exchange(req)
        return res.access_token
