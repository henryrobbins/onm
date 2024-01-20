import os
import shutil
import pytest
from mock import patch
from plaid.api.plaid_api import PlaidApi
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)
from onm import main
from onm.database.database_factory import DatabaseFactory
from onm.link.plaid_link import PlaidLink
from onm.connection.plaid_connection import (
    PlaidConfiguration,
    get_plaid_api,
)
from onm.common import SourceType
from onm.config import Config

pytestmark = pytest.mark.integration

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")
CONFIG_PATH = os.path.join(RESOURCES_PATH, "config.toml")
TEST_DATABASE_PATH = os.path.join(RESOURCES_PATH, "test_plain_text_database")
AMEX_CSV_PATH = os.path.join(RESOURCES_PATH, "amex.csv")
APPLE_CSV_PATH = os.path.join(RESOURCES_PATH, "apple.csv")


class PlaidLinkMock(PlaidLink):
    def __init__(self, get_plaid_api: PlaidApi):
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
            initial_products=[Products("transactions")],
        )
        res = self._plaid_api.sandbox_public_token_create(req)
        return res.public_token

    def _exchange_public_token(self, public_token: str) -> str:
        req = ItemPublicTokenExchangeRequest(public_token)
        res = self._plaid_api.item_public_token_exchange(req)
        return res.access_token


class ConfigMock(Config):
    def __init__(self, config_path: str, plaid_configuration: PlaidConfiguration):
        super().__init__(config_path)
        self._plaid_configuration = plaid_configuration

    def get_plaid_config(self) -> PlaidConfiguration:
        return self._plaid_configuration


@pytest.fixture
def config(client_id: str, secret: str) -> Config:
    plaid_configuration = PlaidConfiguration(
        client_id=client_id, secret=secret, environment="sandbox"
    )
    config = ConfigMock(CONFIG_PATH, plaid_configuration)
    yield config
    if os.path.exists(TEST_DATABASE_PATH):
        shutil.rmtree(TEST_DATABASE_PATH, ignore_errors=True)


def test_plaid_end_to_end(config: Config):
    plaid_api = get_plaid_api(config.get_plaid_config())
    plaid_link_mock = PlaidLinkMock(plaid_api)

    with patch(
        "onm.source.source_factory.LinkFactory.create_link",
        return_value=plaid_link_mock,
    ):
        main.add_source(type=SourceType.PLAID, name="test", config=config)
        main.update_source("test", config)

    main.sync_source("test", config)

    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    transactions = database.get_transactions()
    accounts = database.get_accounts()
    assert len(transactions) > 0
    assert len(accounts) > 0

    # Fetch again (assume nothing changed)
    main.sync_source("test", config)
    assert len(transactions) == len(database.get_transactions())
    assert len(accounts) == len(database.get_accounts())

    # TODO: Add more assertions


def test_amex_csv_end_to_end(config: Config):
    main.add_source(type=SourceType.AMEX_CSV, name="amex", config=config)
    main.update_source("amex", config)
    main.sync_source("amex", config, csv_path=AMEX_CSV_PATH)

    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    transactions = database.get_transactions()
    accounts = database.get_accounts()
    assert 3 == len(transactions)
    assert 1 == len(accounts)

    # Fetch again (assume nothing changed)
    main.sync_source("amex", config, csv_path=AMEX_CSV_PATH)
    assert len(transactions) == len(database.get_transactions())
    assert len(accounts) == len(database.get_accounts())

    # TODO: Add more assertions


def test_apple_csv_end_to_end(config: Config):
    main.add_source(type=SourceType.APPLE_CSV, name="apple", config=config)
    main.update_source("apple", config)
    main.sync_source("apple", config, csv_path=APPLE_CSV_PATH)

    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    transactions = database.get_transactions()
    accounts = database.get_accounts()
    assert 5 == len(transactions)
    assert 1 == len(accounts)

    # Fetch again (assume nothing changed)
    main.sync_source("apple", config, csv_path=APPLE_CSV_PATH)
    assert len(transactions) == len(database.get_transactions())
    assert len(accounts) == len(database.get_accounts())

    # TODO: Add more assertions
