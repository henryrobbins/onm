import os
import pandas as pd
from datetime import datetime
from .database import Database
from ..common import Account, TransactionType, Transaction
from typing import List, Dict

ACCOUNT_DF_COLUMNS = ["name", "balance"]
TRANSACTIONS_DF_COLUMNS = \
    ["date", "description", "amount", "category", "account_name", "type"]

DATE_FMT = r"%Y-%m-%d"

class CsvDatabase(Database):

    def __init__(self, accounts_path: str, transactions_path: str):
        self._accounts_path = accounts_path
        if not os.path.exists(accounts_path):
            os.makedirs(os.path.dirname(accounts_path), exist_ok=True)
            accounts_df = pd.DataFrame(columns=ACCOUNT_DF_COLUMNS)
            self._write_accounts_update(accounts_df)
        self._transactions_path = transactions_path
        if not os.path.exists(transactions_path):
            os.makedirs(os.path.dirname(transactions_path), exist_ok=True)
            transactions_df = pd.DataFrame(columns=TRANSACTIONS_DF_COLUMNS)
            self._write_transactions_update(transactions_df)

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

    def _read_transactions(self) -> pd.DataFrame:
        return pd.read_csv(self._transactions_path)

    def _write_transactions_update(self, transactions_df: pd.DataFrame):
        transactions_df.to_csv(self._transactions_path, index=False)


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
