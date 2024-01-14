import os
import shutil
import pytest
from datetime import datetime
from onm.common import Account, Transaction, TransactionType
from onm.database.csv_database import CsvDatabase
from onm.sync import PlaidSyncCursor
from onm.source.plaid_source import PlaidSource

pytestmark = pytest.mark.unit

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")
DATABASE = os.path.join(RESOURCES_PATH, "csv_database")
TEST_DATABASE = os.path.join(RESOURCES_PATH, "test_csv_database")
NEW_DATABASE = os.path.join(RESOURCES_PATH, "new_csv_database")


ONM_CHECKING = "onm_bank_checking"
ONM_SAVINGS = "onm_bank_savings"

@pytest.fixture
def existing_database():
    shutil.copytree(DATABASE, TEST_DATABASE)
    yield CsvDatabase(TEST_DATABASE)
    if os.path.exists(TEST_DATABASE):
        shutil.rmtree(TEST_DATABASE, ignore_errors=True)


@pytest.fixture
def new_database():
    yield CsvDatabase(NEW_DATABASE)
    if os.path.exists(NEW_DATABASE):
        shutil.rmtree(NEW_DATABASE, ignore_errors=True)


def test_add_account(new_database):
    new_database.add_account(Account("roth_ira", 100.95))
    account = new_database.get_account("roth_ira")
    assert "roth_ira" == account.name
    assert 100.95 == account.balance


def test_get_account(existing_database):
    checking = existing_database.get_account(ONM_CHECKING)
    assert ONM_CHECKING == checking.name
    assert 23.9 == checking.balance
    savings = existing_database.get_account(ONM_SAVINGS)
    assert ONM_SAVINGS == savings.name
    assert 45.6 == savings.balance


def test_get_accounts(existing_database):
    accounts = existing_database.get_accounts()
    assert 2 == len(accounts)


def test_update_account(existing_database):
    existing_database.update_account(Account(ONM_CHECKING, 93.2))
    account = existing_database.get_account(ONM_CHECKING)
    assert 93.2 == account.balance


def test_add_transactions(new_database):
    transaction = Transaction(
        date=datetime(2024,3,12).date(),
        description="TOMI JAZZ",
        amount=35.8,
        category="MUSIC",
        account_name="onm_bank",
        type=TransactionType.DEBIT
    )
    new_database.add_transactions([transaction])
    transactions = new_database.get_transactions()
    assert 1 == len(transactions)
    transaction = transactions[0]
    assert datetime(2024,3,12).date() == transaction.date
    assert "TOMI JAZZ" == transaction.description
    assert 35.8 == transaction.amount
    assert "MUSIC" == transaction.category
    assert "onm_bank" == transaction.account_name
    assert TransactionType.DEBIT == transaction.type


def test_get_transactions(existing_database):
    transactions = existing_database.get_transactions()
    assert 1 == len(transactions)
    transaction = transactions[0]
    assert datetime(2024,12,3).date() == transaction.date
    assert "UMPHREYS" == transaction.description
    assert 102.8 == transaction.amount
    assert "MUSIC" == transaction.category
    assert "onm_savings" == transaction.account_name
    assert TransactionType.DEBIT == transaction.type


def test_set_sync_cursor(new_database):
    source = PlaidSource("test_source")
    expected_sync_cursor = PlaidSyncCursor("805c4d192e0d4bbe742bda1f21fc5bbc")
    new_database.set_sync_cursor(source, expected_sync_cursor)
    sync_cursor = new_database.get_sync_cursor(source)
    assert expected_sync_cursor.cursor == sync_cursor.cursor


def test_get_sync_cursor(existing_database):
    source = PlaidSource("onm_bank")
    sync_cursor = existing_database.get_sync_cursor(source)
    assert "75626d959a12ead47337eca9d9c6eaec" == sync_cursor.cursor

    new_source = PlaidSource("bank")
    sync_cursor = existing_database.get_sync_cursor(new_source)
    assert sync_cursor is None
