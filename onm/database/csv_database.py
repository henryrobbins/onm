import os
import json
import pandas as pd
from datetime import datetime
from onm.source.source import Source
from onm.sync import SyncCursor, create_sync_cursor, get_sync_cursor_type_from
from .database import Database
from ..common import Account, TransactionType, Transaction
from typing import List, Dict

ACCOUNTS = "accounts.csv"
TRANSACTIONS = "transactions.csv"
CURSORS = "cursors.csv"

ACCOUNT_DF_COLUMNS = ["name", "balance"]
TRANSACTIONS_DF_COLUMNS = \
    ["date", "description", "amount", "category", "account_name", "type"]
CURSOR_TYPE = "type"
CURSOR_DATA = "data"
CURSORS_DF_COLUMNS = [CURSOR_TYPE, CURSOR_DATA]

DATE_FMT = r"%Y-%m-%d"


class CsvDatabase(Database):

    def __init__(self, database_path: str):
        self._accounts_path = os.path.join(database_path, ACCOUNTS)
        if not os.path.exists(self._accounts_path):
            os.makedirs(os.path.dirname(self._accounts_path), exist_ok=True)
            accounts_df = pd.DataFrame(columns=ACCOUNT_DF_COLUMNS)
            self._write_accounts_update(accounts_df)

        self._transactions_path = os.path.join(database_path, TRANSACTIONS)
        if not os.path.exists(self._transactions_path):
            os.makedirs(os.path.dirname(self._transactions_path), exist_ok=True)
            transactions_df = pd.DataFrame(columns=TRANSACTIONS_DF_COLUMNS)
            self._write_transactions_update(transactions_df)

        self._cursors_path = os.path.join(database_path, CURSORS)
        if not os.path.exists(self._cursors_path):
            os.makedirs(os.path.dirname(self._cursors_path), exist_ok=True)
            cursors_df = pd.DataFrame(columns=CURSORS_DF_COLUMNS)
            cursors_df.to_csv(self._cursors_path)

    def add_account(self, account: Account):
        accounts_df = self._read_accounts()
        accounts_df.loc[account.name] = account._asdict()
        self._write_accounts_update(accounts_df)

    def get_account(self, name: str) -> Account:
        accounts_df = self._read_accounts()
        try:
            account = accounts_df.loc[name]
        except KeyError:
            raise ValueError(f"Account '{name}' is not in the database")
        return Account(**account)

    def get_accounts(self) -> List[Account]:
        accounts_df = self._read_accounts()
        return [Account(**row) for _, row in accounts_df.iterrows()]

    def update_account(self, account: Account):
        accounts_df = self._read_accounts()
        try:
            accounts_df.loc[account.name] = account._asdict()
        except KeyError:
            raise ValueError(f"Account '{account.name}' is not in the database")
        self._write_accounts_update(accounts_df)

    def _read_accounts(self) -> pd.DataFrame:
        return pd.read_csv(self._accounts_path, index_col=0)

    def _write_accounts_update(self, accounts_df: pd.DataFrame):
        accounts_df.to_csv(self._accounts_path)

    def add_transactions(self, transactions: List[Transaction]):
        transactions_df = self._read_transactions()
        new_transactions_df = pd.DataFrame([_transaction_dict(t) for t in transactions])
        transactions_df = pd.concat([transactions_df, new_transactions_df])
        self._write_transactions_update(transactions_df)

    def get_transactions(self) -> List[Transaction]:
        transactions_df = self._read_transactions()
        return [_transaction_from(row) for _, row in transactions_df.iterrows()]

    def set_sync_cursor(self, source: Source, sync_cursor: SyncCursor):
        cursors = self._read_cursors()
        cursors[source.name] = sync_cursor
        self._write_cursors_update(cursors)

    def get_sync_cursor(self, source: Source) -> SyncCursor:
        cursors = self._read_cursors()
        return cursors.get(source.name, None)

    def _read_transactions(self) -> pd.DataFrame:
        return pd.read_csv(self._transactions_path)

    def _write_transactions_update(self, transactions_df: pd.DataFrame):
        transactions_df.to_csv(self._transactions_path, index=False)

    def _read_cursors(self) -> Dict[str, SyncCursor]:
        cursors_df = pd.read_csv(self._cursors_path, index_col=0)
        cursors = {}
        for index, row in cursors_df.iterrows():
            data = json.loads(row[CURSOR_DATA])
            cursors[index] = create_sync_cursor(row[CURSOR_TYPE], data)
        return cursors

    def _write_cursors_update(self, cursors: Dict[str, SyncCursor]):
        cursors_dict = {}
        for source_name, cursor in cursors.items():
            cursors_dict[source_name] = {
                CURSOR_TYPE: get_sync_cursor_type_from(cursor).value,
                CURSOR_DATA: json.dumps(cursor.as_dict())
            }
        cursors_df = pd.DataFrame.from_dict(cursors_dict, orient='index')
        cursors_df.to_csv(self._cursors_path)


def _transaction_dict(transaction: Transaction) -> Dict:
    return {
        "date": transaction.date.strftime(DATE_FMT),
        "description": transaction.description,
        "amount": transaction.amount,
        "category": transaction.category,
        "account_name": transaction.account_name,
        "type": transaction.type.value
    }


def _transaction_from(dict: Dict) -> Transaction:
    return Transaction(
        date= datetime.strptime(dict["date"], DATE_FMT).date(),
        description= dict["description"],
        amount=dict["amount"],
        category=dict["category"],
        account_name=dict["account_name"],
        type=TransactionType(dict["type"])
    )
