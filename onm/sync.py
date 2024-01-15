from abc import ABC
from enum import Enum
from datetime import datetime
from typing import Dict


class SyncCursorType(Enum):
    PLAID = "plaid"
    CSV = "csv"


class SyncCursor(ABC):
    pass


class PlaidSyncCursor(SyncCursor):
    def __init__(self, cursor: str):
        self._cursor = cursor

    @property
    def cursor(self) -> str:
        return self._cursor

    def as_dict(self) -> Dict:
        return {"cursor": self._cursor}


class CsvSyncCursor(SyncCursor):
    def __init__(self, latest_transaction_date: str):
        self._latest_transaction_date = datetime.fromisoformat(
            latest_transaction_date
        ).date()

    @property
    def latest_transaction_date(self) -> str:
        return self._latest_transaction_date

    def as_dict(self) -> Dict:
        return {"latest_transaction_date": self._latest_transaction_date.isoformat()}


def create_sync_cursor(type: str, data: Dict) -> SyncCursor:
    sync_cursor_type = SyncCursorType(type)
    if sync_cursor_type == SyncCursorType.PLAID:
        return PlaidSyncCursor(**data)
    elif sync_cursor_type == SyncCursorType.CSV:
        return CsvSyncCursor(**data)
    else:
        raise ValueError("unknown error")


def get_sync_cursor_type_from(sync_cursor: SyncCursor):
    if type(sync_cursor) is PlaidSyncCursor:
        return SyncCursorType.PLAID
    elif type(sync_cursor) is CsvSyncCursor:
        return SyncCursorType.CSV
    else:
        raise ValueError("Unknown sync cursor type")
