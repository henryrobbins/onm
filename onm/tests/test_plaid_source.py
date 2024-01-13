import pytest
from mock import patch
from unittest.mock import Mock
from datetime import datetime
from onm.connection.plaid_connection import PlaidConnection
from onm.connection import connection
from onm.connection.connection import AccountBalance, Transaction
from onm.common import TransactionType
from onm.source.plaid_source import PlaidSourceFactory
from onm.source.source import SyncTransactionsResponse
from onm.sync import PlaidSyncCursor

pytestmark = pytest.mark.unit

ACCESS_TOKEN = "access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77"


@pytest.fixture
def plaid_connection_mock():

    plaid_connection = Mock(PlaidConnection)

    account = AccountBalance(
        account_name="ONM CHECKING",
        account_id="e02fc823810d73a9127d00948ab000d4",
        balance=0.0
    )

    def get_account_balances_side_effect(*args):
        if args[0] == ACCESS_TOKEN:
            return [account]
        return None

    plaid_connection.get_account_balances.side_effect = \
        get_account_balances_side_effect

    transaction = Transaction(
        date=datetime(2024, 1, 13).date(),
        description="TOMI JAZZ",
        amount=89.3,
        category="MUSIC",
        account_id="e02fc823810d73a9127d00948ab000d4",
        type=connection.TransactionType.DEBIT
    )

    def sync_transactions_side_effect(*args, **kwargs):
        if kwargs["access_token"] == ACCESS_TOKEN:
            return SyncTransactionsResponse(
                transactions=[transaction],
                sync_cursor=PlaidSyncCursor(cursor="fd463d42b92c62fc5aa8f73db68c7e2d")
            )
        return None

    plaid_connection.sync_transactions.side_effect = \
        sync_transactions_side_effect

    return plaid_connection


def test_plaid_source(plaid_connection_mock):
    plaid_source = PlaidSourceFactory.create_source(
        name = "test",
        access_token = ACCESS_TOKEN,
        plaid_connection = plaid_connection_mock
    )

    account_balances = plaid_source.get_account_balances(plaid_connection_mock)
    assert 1 == len(account_balances)
    assert 0.0 == account_balances["ONM CHECKING"]

    sync_cursor = PlaidSyncCursor(cursor="c4498331dfe9edf14bf28e5ab6f51e58")
    res = plaid_source.sync_transactions(
            connection=plaid_connection_mock,
            sync_cursor=sync_cursor
        )
    assert "fd463d42b92c62fc5aa8f73db68c7e2d" == res.sync_cursor.cursor
    assert 1 == len(res.transactions)
    transaction = res.transactions[0]
    assert datetime(2024, 1, 13).date() == transaction.date
    assert "TOMI JAZZ" == transaction.description
    assert 89.3 == transaction.amount
    assert "MUSIC" == transaction.category
    assert "ONM CHECKING" == transaction.account_name
    assert TransactionType.DEBIT == transaction.type
