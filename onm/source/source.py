from abc import ABC, abstractmethod
from typing import List, Dict, NamedTuple, Optional
from ..common import Transaction
from ..sync import SyncCursor
from ..connection.connection import Connection


class SyncTransactionsResponse(NamedTuple):
    transactions: List[Transaction]
    sync_cursor: SyncCursor


class Source(ABC):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_account_balances(self, connection: Connection) -> Dict[str, float]:
        pass

    @abstractmethod
    def sync_transactions(self, connection: Connection, sync_cursor: Optional[SyncCursor]) -> SyncTransactionsResponse:
        pass


class SourceFactory(ABC):

    @abstractmethod
    def create_source(self) -> Source:
        pass
