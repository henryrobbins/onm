from enum import Enum
from abc import ABC, abstractmethod
from ..common import Account, Transaction
from ..sync import SyncCursor
from ..source.source import Source
from typing import List, Optional


class DatabaseType(Enum):
    CSV="csv"


class Database(ABC):

    @abstractmethod
    def add_account(self, account: Account):
        pass

    @abstractmethod
    def get_account(self, name: str) -> Account:
        pass

    @abstractmethod
    def get_accounts(self) -> List[Account]:
        pass

    @abstractmethod
    def update_account(self, account: Account):
        pass

    @abstractmethod
    def add_transactions(self, transactions: List[Transaction]):
        pass

    @abstractmethod
    def get_transactions(self) -> List[Transaction]:
        pass

    @abstractmethod
    def set_sync_cursor(self, source: Source, sync_cursor: SyncCursor):
        pass

    @abstractmethod
    def get_sync_cursor(self, source: Source) -> Optional[SyncCursor]:
        pass
