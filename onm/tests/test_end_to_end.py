import os
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
from onm.config import Config

pytestmark = pytest.mark.integration

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")
CONFIG_PATH = os.path.join(RESOURCES_PATH, "config.ini")
# DATABASE_PATH = os.path.join(RESOURCES_PATH, "csv_database")


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

    config = Config(CONFIG_PATH)

    # Create new source
    plaid_api = get_plaid_api(plaid_configuration)
    link_factory_mock = Mock(LinkFactory)
    link_factory_mock.create_link.return_value = PlaidLinkMock(plaid_api)
    plaid_source = SourceFactory.create_source(
        type= SourceType.PLAID,
        name= "test",
        link_factory=link_factory_mock,
        plaid_api=plaid_api
    )
    plaid_source.update_link(link_factory_mock)

    # Add to sources
    sources = config.get_sources()
    sources.add_source(plaid_source)

    # Get source
    source = sources.get_source("test")
    plaid_connection = PlaidConnection(plaid_api)
    account_balances = source.get_account_balances(plaid_connection)
    sync_transactions_res = source.sync_transactions(plaid_connection)

    # Write to fake database
    database = config.get_database()
    transactions = sync_transactions_res.transactions
    sync_cursor = sync_transactions_res.sync_cursor
    database.add_transactions(transactions)
    database.set_sync_cursor(source, sync_cursor)

    from_db_transactions = database.get_transactions()
    assert len(transactions) == len(from_db_transactions)

    # Fetch again (assume nothing changed)
    sync_transactions_res = source.sync_transactions(plaid_connection, sync_cursor)
    transactions = sync_transactions_res.transactions
    sync_cursor = sync_transactions_res.sync_cursor
    assert 0 == len(transactions)

    # TODO: Add more assertions
