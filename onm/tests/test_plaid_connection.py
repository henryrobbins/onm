import pytest
from mock import patch
from unittest.mock import Mock
from datetime import datetime
from plaid import Environment
from plaid.api.plaid_api import PlaidApi
from plaid.model.account_base import AccountBase
from plaid.model.account_balance import AccountBalance
from plaid.model.transaction import Transaction
from plaid.model.personal_finance_category import PersonalFinanceCategory
from plaid.model.link_token_create_response import LinkTokenCreateResponse
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from plaid.model.item_public_token_exchange_response import ItemPublicTokenExchangeResponse
from plaid.model.accounts_get_response import AccountsGetResponse
from onm.connection.plaid_connection import TransactionType, PlaidConnection, PlaidConfiguration, PlaidLink, get_plaid_api
from onm.sync import PlaidSyncCursor

pytestmark = pytest.mark.unit

TEST_CLIENT_ID = "e138bf64a485f76090e044defe479044"
TEST_SECRET = "fdf118ab6cc2e3aba0798f9bf5f8abca"
TEST_ENVIRONMENT = "sandbox"

LINK_TOKEN = "link-sandbox-cd3f30bf-cd14-43f8-9355-a5a48f3ed700"
PUBLIC_TOKEN = "public-sandbox-a05be323-564f-48c7-bbcb-57dd426efe3c"
ACCESS_TOKEN = "access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77"

@pytest.fixture
def plaid_configuration():
    return PlaidConfiguration(
        client_id = TEST_CLIENT_ID,
        secret = TEST_SECRET,
        environment = TEST_ENVIRONMENT
    )


def test_get_plaid_api(plaid_configuration):
    plaid_api = get_plaid_api(plaid_configuration)
    assert PlaidApi == type(plaid_api)
    config = plaid_api.api_client.configuration
    assert Environment.Sandbox == config.host
    assert TEST_CLIENT_ID == config.api_key["clientId"]
    assert TEST_SECRET == config.api_key["secret"]


@patch('onm.webserver.serve')
def test_plaid_link_get_access_token(webserver_serve_mock):
    plaid_api = Mock(PlaidApi)

    link_token_res = Mock(LinkTokenCreateResponse)
    link_token_res.configure_mock(link_token=LINK_TOKEN)
    plaid_api.link_token_create.return_value = link_token_res

    def webserver_serve_mock_side_effect(**kwargs):
        if (kwargs.get("token") == LINK_TOKEN and
            kwargs.get("type") == "link" and
            kwargs.get("clientName") == "onm" and
            kwargs.get("pageTitle") == "Link Account Credentials"):
            return {"public_token": PUBLIC_TOKEN}
        return {}

    webserver_serve_mock.side_effect = webserver_serve_mock_side_effect

    token_exchange_res = Mock(ItemPublicTokenExchangeResponse)
    token_exchange_res.configure_mock(access_token=ACCESS_TOKEN)

    def token_exchange_side_effect(*args):
        req = args[0]
        if req.public_token == PUBLIC_TOKEN:
            return token_exchange_res
        return None

    plaid_api.item_public_token_exchange.side_effect = \
        token_exchange_side_effect

    plaid_link = PlaidLink(plaid_api)
    assert ACCESS_TOKEN == plaid_link.get_access_token()


@patch('onm.webserver.serve')
def test_plaid_link_update_link(webserver_serve_mock):
    plaid_api = Mock(PlaidApi)

    link_token_res = Mock(LinkTokenCreateResponse)
    link_token_res.configure_mock(link_token=LINK_TOKEN)

    def link_token_create_side_effect(*args):
        req = args[0]
        if req.access_token == ACCESS_TOKEN:
            return link_token_res
        return None

    plaid_api.link_token_create.side_effect = link_token_create_side_effect

    plaid_link = PlaidLink(plaid_api)
    plaid_link.update_link(ACCESS_TOKEN)

    webserver_serve_mock.assert_called_with(
        clientName="onm",
        pageTitle="Update Account Credentials",
        type="update",
        token=LINK_TOKEN
    )


@pytest.fixture
def plaid_api_mock():
    plaid_api = Mock(PlaidApi)

    balance = Mock(AccountBalance)
    balance.configure_mock(current=131.17)
    account = Mock(AccountBase)
    account.configure_mock(
        official_name="ONM Bank",
        name="onm",
        account_id="bc3eb2e652219571d5897b8422869388",
        balances=balance
    )
    accounts = [account]
    accounts_get_res = Mock(AccountsGetResponse)
    accounts_get_res.configure_mock(accounts=accounts)

    def accounts_balance_get_side_effect(*args):
        req = args[0]
        if req.access_token == ACCESS_TOKEN:
            return accounts_get_res
        return None

    plaid_api.accounts_balance_get.side_effect = accounts_balance_get_side_effect

    personal_finance_category = Mock(PersonalFinanceCategory)
    personal_finance_category.configure_mock(
        primary="ENTERTAINMENT",
        detailed="MUSIC"
    )

    transaction = Mock(Transaction)
    transaction.configure_mock(
        date= datetime(2024, 1, 13).date(),
        name="TOMI JAZZ",
        amount=-78.9,
        personal_finance_category=personal_finance_category,
        account_id="bc3eb2e652219571d5897b8422869388"
    )

    transactions = [transaction]
    transactions_sync_res = Mock(TransactionsSyncResponse)
    transactions_sync_res.configure_mock(
        has_more=False,
        next_cursor="",
        added=transactions
    )

    def transactions_sync_side_effect(*args):
        req = args[0]
        if req.access_token == ACCESS_TOKEN:
            return transactions_sync_res
        return None

    plaid_api.transactions_sync.side_effect = transactions_sync_side_effect

    return plaid_api


def test_plaid_connection_get_account_balances(plaid_api_mock):
    plaid_connection = PlaidConnection(plaid_api_mock)
    account_balances = plaid_connection.get_account_balances(ACCESS_TOKEN)
    assert 1 == len(account_balances)
    account = account_balances[0]
    assert "ONM Bank" == account.account_name
    assert "bc3eb2e652219571d5897b8422869388" == account.account_id
    assert 131.17 == account.balance


def test_plaid_connection_get_new_transactions(plaid_api_mock):
    plaid_connection = PlaidConnection(plaid_api_mock)
    sync_cursor = PlaidSyncCursor(cursor="c4498331dfe9edf14bf28e5ab6f51e58")
    res = plaid_connection.sync_transactions(
        sync_cursor=sync_cursor,
        access_token=ACCESS_TOKEN
    )
    new_sync_cursor = res.sync_cursor
    transactions = res.transactions
    assert 1 == len(transactions)
    transaction = transactions[0]
    assert datetime(2024, 1, 13).date() == transaction.date
    assert "TOMI JAZZ" == transaction.description
    assert 78.9 == transaction.amount
    assert TransactionType.DEBIT == transaction.type
    assert "ENTERTAINMENT:MUSIC" == transaction.category
    assert "bc3eb2e652219571d5897b8422869388" == transaction.account_id
