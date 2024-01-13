from abc import ABC

class SyncCursor(ABC):
    pass


class PlaidSyncCursor(SyncCursor):

    def __init__(self, cursor: str):
        self._cursor = cursor

    @property
    def cursor(self) -> str:
        return self._cursor
