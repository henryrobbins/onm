import pytest
from unittest.mock import Mock
from plaid.api.plaid_api import PlaidApi
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from onm.link.link_factory import LinkFactory
from onm.link.plaid_link import PlaidLink
from onm.connection.plaid_connection import PlaidConnection, PlaidConfiguration, get_plaid_api
from onm.source.source_factory import SourceFactory
from onm.common import SourceType

pytestmark = pytest.mark.integration


class PlaidLinkMock(PlaidLink):

    def __init__(self, get_plaid_api : PlaidApi):
        self._plaid_api = get_plaid_api

    def get_access_token(self):
        public_token = self._get_public_token()
        access_token = self._exchange_public_token(public_token)
        return access_token

    def update_link(self, access_token: str):
        pass

    def _get_public_token(self) -> str:
        req = SandboxPublicTokenCreateRequest(
            # https://plaid.com/docs/sandbox/institutions/
            institution_id="ins_109508",
            initial_products=[Products('transactions')]
        )
        res = self._plaid_api.sandbox_public_token_create(req)
        return res.public_token

    def _exchange_public_token(self, public_token: str) -> str:
        req = ItemPublicTokenExchangeRequest(public_token)
        res = self._plaid_api.item_public_token_exchange(req)
        return res.access_token


@pytest.fixture
def plaid_configuration(client_id, secret):
    return PlaidConfiguration(
        client_id=client_id,
        secret=secret,
        environment="sandbox"
    )


def test_end_to_end(plaid_configuration):
    plaid_api = get_plaid_api(plaid_configuration)
    link_factory_mock = Mock(LinkFactory)
    link_factory_mock.create_link.return_value = PlaidLinkMock(plaid_api)

    plaid_source = SourceFactory.create_source(
        type= SourceType.PLAID,
        name= "test",
        link_factory=link_factory_mock,
        plaid_api=plaid_api
    )

    # plaid_connection = PlaidConnection(plaid_api)
    # account_balances = plaid_source.get_account_balances(plaid_connection)
    # print(account_balances)
    # transactions = plaid_source.sync_transactions(plaid_connection)
    # print(transactions)

    plaid_source.update_link(link_factory_mock)

    # TODO: Add assertions
