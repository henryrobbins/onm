from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, NamedTuple, Optional
from ..common import Transaction, Account, SourceType
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

    @property
    def type(self) -> SourceType:
        pass

    @abstractmethod
    def get_account_balances(self, connection: Connection) -> List[Account]:
        pass

    @abstractmethod
    def sync_transactions(
        self, connection: Connection, sync_cursor: Optional[SyncCursor]
    ) -> SyncTransactionsResponse:
        pass

    @abstractmethod
    def serialize(self) -> Dict:
        pass

    @abstractmethod
    def deserialize(self, data: Dict) -> Source:
        pass
