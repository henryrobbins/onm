import pytest
from mock import patch
from unittest.mock import Mock
from plaid import Environment
from plaid.api.plaid_api import PlaidApi
from plaid.model.link_token_create_response import LinkTokenCreateResponse
from plaid.model.item_public_token_exchange_response import ItemPublicTokenExchangeResponse
from onm.source.plaid_source import PlaidConfiguration, PlaidLink, get_plaid_api

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


def test_plaid_configuration(plaid_configuration):
    assert TEST_CLIENT_ID == plaid_configuration.client_id
    assert TEST_SECRET == plaid_configuration.secret
    assert TEST_ENVIRONMENT == plaid_configuration.environment


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


# TODO: test_plaid_source_get_account_balances
# TODO: get_new_transactions
