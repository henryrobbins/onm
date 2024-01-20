import os
import shutil
import pytest
from datetime import datetime
from onm.common import Account, Transaction, TransactionType
from onm.database.plain_text_database import PlainTextDatabase
from onm.sync import PlaidSyncCursor
from onm.source.plaid_source import PlaidSource

pytestmark = pytest.mark.unit

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")
DATABASE = os.path.join(RESOURCES_PATH, "plain_text_database")
TEST_DATABASE = os.path.join(RESOURCES_PATH, "test_plain_text_database")
NEW_DATABASE = os.path.join(RESOURCES_PATH, "new_plain_text_database")


ONM_CHECKING = "onm_bank_checking"
ONM_SAVINGS = "onm_bank_savings"


@pytest.fixture
def existing_database() -> PlainTextDatabase:
    shutil.copytree(DATABASE, TEST_DATABASE)
    yield PlainTextDatabase(TEST_DATABASE)
    if os.path.exists(TEST_DATABASE):
        shutil.rmtree(TEST_DATABASE, ignore_errors=True)


@pytest.fixture
def new_database() -> PlainTextDatabase:
    yield PlainTextDatabase(NEW_DATABASE)
    if os.path.exists(NEW_DATABASE):
        shutil.rmtree(NEW_DATABASE, ignore_errors=True)


def test_add_account(new_database: PlainTextDatabase):
    new_database.add_account(Account("roth_ira", 100.95))
    account = new_database.get_account("roth_ira")
    assert "roth_ira" == account.name
    assert 100.95 == account.balance


def test_get_account(existing_database: PlainTextDatabase):
    checking = existing_database.get_account(ONM_CHECKING)
    assert ONM_CHECKING == checking.name
    assert 23.9 == checking.balance
    savings = existing_database.get_account(ONM_SAVINGS)
    assert ONM_SAVINGS == savings.name
    assert 45.6 == savings.balance


def test_get_accounts(existing_database: PlainTextDatabase):
    accounts = existing_database.get_accounts()
    assert 2 == len(accounts)


def test_update_account(existing_database: PlainTextDatabase):
    existing_database.update_account(Account(ONM_CHECKING, 93.2))
    account = existing_database.get_account(ONM_CHECKING)
    assert 93.2 == account.balance


def test_add_transactions(new_database: PlainTextDatabase):
    transaction = Transaction(
        date=datetime(2024, 3, 12).date(),
        description="TOMI JAZZ",
        amount=35.8,
        category="MUSIC",
        account_name="onm_bank",
        type=TransactionType.DEBIT,
    )
    new_database.add_transactions([transaction])
    transactions = new_database.get_transactions()
    assert 1 == len(transactions)
    transaction = transactions[0]
    assert datetime(2024, 3, 12).date() == transaction.date
    assert "TOMI JAZZ" == transaction.description
    assert 35.8 == transaction.amount
    assert "MUSIC" == transaction.category
    assert "onm_bank" == transaction.account_name
    assert TransactionType.DEBIT == transaction.type


def test_get_transactions(existing_database: PlainTextDatabase):
    transactions = existing_database.get_transactions()
    assert 1 == len(transactions)
    transaction = transactions[0]
    assert datetime(2024, 12, 3).date() == transaction.date
    assert "UMPHREYS" == transaction.description
    assert 102.8 == transaction.amount
    assert "MUSIC" == transaction.category
    assert "onm_savings" == transaction.account_name
    assert TransactionType.DEBIT == transaction.type


def test_set_sync_cursor(new_database: PlainTextDatabase):
    source = PlaidSource("test_source")
    expected_sync_cursor = PlaidSyncCursor("805c4d192e0d4bbe742bda1f21fc5bbc")
    new_database.set_sync_cursor(source, expected_sync_cursor)
    sync_cursor = new_database.get_sync_cursor(source)
    assert expected_sync_cursor.cursor == sync_cursor.cursor


def test_get_sync_cursor(existing_database: PlainTextDatabase):
    source = PlaidSource("onm_bank")
    sync_cursor = existing_database.get_sync_cursor(source)
    assert "75626d959a12ead47337eca9d9c6eaec" == sync_cursor.cursor

    new_source = PlaidSource("bank")
    sync_cursor = existing_database.get_sync_cursor(new_source)
    assert sync_cursor is None


def test_get_source(existing_database: PlainTextDatabase):
    source = existing_database.get_source("platypus_bank")
    assert PlaidSource == type(source)
    assert "access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77" == source.access_token
    account_id_map = source.account_id_map
    assert "checking" == account_id_map["6886e1c6916351f894255ef738176744"]
    assert "savings" == account_id_map["9217d6c969ac114533812fdacb15b11a"]


def test_sources_add_plaid_source(new_database: PlainTextDatabase):
    source = PlaidSource(
        name="onm_bank",
        access_token="access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77",
        account_id_map={
            "a927faed81ca48916e56e6ccda63fe09": "checking",
            "76b069b74b582f62f4890a88b14402a6": "savings",
        },
    )
    new_database.add_source(source)

    source = new_database.get_source("onm_bank")
    assert PlaidSource == type(source)
    assert "access-sandbox-a4a6c36b-0276-431d-a843-65c30b506e77" == source.access_token
    account_id_map = source.account_id_map
    assert "checking" == account_id_map["a927faed81ca48916e56e6ccda63fe09"]
    assert "savings" == account_id_map["76b069b74b582f62f4890a88b14402a6"]
