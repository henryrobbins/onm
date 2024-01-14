from abc import ABC
from enum import Enum
from typing import Dict


class SyncCursorType(Enum):
    PLAID="plaid"


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


def create_sync_cursor(type: str, data: Dict) -> SyncCursor:
    sync_cursor_type = SyncCursorType(type)
    if sync_cursor_type == SyncCursorType.PLAID:
        return PlaidSyncCursor(**data)
    else:
        raise ValueError(f"unknown error")


def get_sync_cursor_type_from(sync_cursor: SyncCursor):
    if type(sync_cursor) == PlaidSyncCursor:
        return SyncCursorType.PLAID
    else:
        raise ValueError(f"Unknown sync cursor type")
