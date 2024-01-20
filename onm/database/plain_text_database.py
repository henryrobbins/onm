import os
import json
import tomlkit
import pandas as pd
from datetime import datetime
from onm.source.source import Source
from onm.source.plaid_source import PlaidSource
from onm.source.csv_source import AppleCsvSource, AmexCsvSource
from onm.sync import SyncCursor, create_sync_cursor, get_sync_cursor_type_from
from .database import Database
from onm.common import SourceType, Account, TransactionType, Transaction
from typing import List, Dict, Optional

ACCOUNTS = "accounts.csv"
TRANSACTIONS = "transactions.csv"
CURSORS = "cursors.csv"
SOURCES = "sources.toml"

ACCOUNT_DF_COLUMNS = ["name", "balance"]
TRANSACTIONS_DF_COLUMNS = [
    "date",
    "description",
    "amount",
    "category",
    "account_name",
    "type",
]
CURSOR_TYPE = "type"
CURSOR_DATA = "data"
CURSORS_DF_COLUMNS = [CURSOR_TYPE, CURSOR_DATA]

SOURCE_TYPE = "type"
ACCESS_TOKEN = "access_token"
ACCOUNT_ID_MAP = "account_id_map"

DATE_FMT = r"%Y-%m-%d"


class PlainTextDatabase(Database):
    def __init__(
        self,
        database_path: str,
        accounts_path: str = None,
        transactions_path: str = None,
        cursors_path: str = None,
        sources_path: str = None,
    ):
        self._accounts_path = PlainTextDatabase._setup_path(
            database_path, ACCOUNTS, accounts_path
        )
        if not os.path.exists(self._accounts_path):
            os.makedirs(os.path.dirname(self._accounts_path), exist_ok=True)
            accounts_df = pd.DataFrame(columns=ACCOUNT_DF_COLUMNS)
            self._write_accounts_update(accounts_df)

        self._transactions_path = PlainTextDatabase._setup_path(
            database_path, TRANSACTIONS, transactions_path
        )
        if not os.path.exists(self._transactions_path):
            os.makedirs(os.path.dirname(self._transactions_path), exist_ok=True)
            transactions_df = pd.DataFrame(columns=TRANSACTIONS_DF_COLUMNS)
            self._write_transactions_update(transactions_df)

        self._cursors_path = PlainTextDatabase._setup_path(
            database_path, CURSORS, cursors_path
        )
        if not os.path.exists(self._cursors_path):
            os.makedirs(os.path.dirname(self._cursors_path), exist_ok=True)
            cursors_df = pd.DataFrame(columns=CURSORS_DF_COLUMNS)
            cursors_df.to_csv(self._cursors_path)

        self._sources_path = PlainTextDatabase._setup_path(
            database_path, SOURCES, sources_path
        )
        if not os.path.exists(self._sources_path):
            os.makedirs(os.path.dirname(self._sources_path), exist_ok=True)
            with open(self._sources_path, "w") as _:
                pass

    @staticmethod
    def _setup_path(
        database_path: str, default_filename: str, override_path: Optional[str]
    ) -> str:
        if override_path is not None:
            return override_path
        return os.path.join(database_path, default_filename)

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
                CURSOR_DATA: json.dumps(cursor.as_dict()),
            }
        cursors_df = pd.DataFrame.from_dict(cursors_dict, orient="index")
        cursors_df.to_csv(self._cursors_path)

    def add_source(self, source: Source):
        sources_config = self._read_sources()
        if source.type == SourceType.PLAID:
            self._add_plaid_source(source, sources_config)
        elif source.type == SourceType.AMEX_CSV:
            self._add_csv_source(source, sources_config)
        elif source.type == SourceType.APPLE_CSV:
            self._add_csv_source(source, sources_config)
        else:
            raise ValueError("Unsupported source")
        self._write_sources_update(sources_config)

    def _add_plaid_source(
        self, source: PlaidSource, sources_config: tomlkit.TOMLDocument
    ):
        source_config = tomlkit.table()
        source_config.add(SOURCE_TYPE, source.type.value)
        source_config.add(ACCESS_TOKEN, source.access_token)
        accounts = tomlkit.array()
        ts = []
        for account_id, account_name in source.account_id_map.items():
            t = tomlkit.inline_table()
            t.add("id", account_id)
            t.add("name", account_name)
            ts.append(t)
        accounts.extend(ts)
        source_config.add(ACCOUNT_ID_MAP, accounts.multiline(True))
        sources_config.add(source.name, source_config)

    def _add_csv_source(self, source: Source, sources_config: tomlkit.TOMLDocument):
        source_config = tomlkit.table()
        source_config.add(SOURCE_TYPE, source.type.value)
        sources_config.add(source.name, source_config)

    def get_source(self, name: str) -> Source:
        # if not self._config.has_section(name):
        #     raise ValueError(f"Source '{name}' does not exist")
        sources_config = self._read_sources()
        source_config = sources_config.get(name)
        source_type = SourceType(source_config.get(SOURCE_TYPE))
        if source_type == SourceType.PLAID:
            return self._get_plaid_source(name, source_config)
        elif source_type == SourceType.AMEX_CSV:
            return AmexCsvSource(name)
        elif source_type == SourceType.APPLE_CSV:
            return AppleCsvSource(name)
        else:
            raise ValueError("Unsupported source")

    def _get_plaid_source(self, name: str, source_config: Dict) -> PlaidSource:
        account_id_map = {}
        for account in source_config.get(ACCOUNT_ID_MAP):
            account_id_map[account.get("id")] = account.get("name")
        return PlaidSource(
            name=name,
            access_token=source_config.get(ACCESS_TOKEN),
            account_id_map=account_id_map,
        )

    def _read_sources(self) -> tomlkit.TOMLDocument:
        with open(self._sources_path, mode="rt", encoding="utf-8") as fp:
            return tomlkit.load(fp)

    def _write_sources_update(self, sources_config: tomlkit.TOMLDocument):
        with open(self._sources_path, mode="wt", encoding="utf-8") as fp:
            tomlkit.dump(sources_config, fp)


def _transaction_dict(transaction: Transaction) -> Dict:
    return {
        "date": transaction.date.strftime(DATE_FMT),
        "description": transaction.description,
        "amount": transaction.amount,
        "category": transaction.category,
        "account_name": transaction.account_name,
        "type": transaction.type.value,
    }


def _transaction_from(dict: Dict) -> Transaction:
    return Transaction(
        date=datetime.strptime(dict["date"], DATE_FMT).date(),
        description=dict["description"],
        amount=dict["amount"],
        category=dict["category"],
        account_name=dict["account_name"],
        type=TransactionType(dict["type"]),
    )