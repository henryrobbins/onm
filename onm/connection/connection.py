from datetime import date
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Optional
from ..sync import SyncCursor


class AccountBalance(NamedTuple):
    account_name: str
    account_id: str
    balance: float


class TransactionType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class Transaction(NamedTuple):
    date: date
    description: str
    amount: float
    primary_category: str
    detailed_category: str
    account_id: str
    type: TransactionType


class SyncTransactionsResponse(NamedTuple):
    transactions: List[Transaction]
    sync_cursor: SyncCursor


class Connection(ABC):
    @abstractmethod
    def get_account_balances(self, access_token: Optional[str]) -> List[AccountBalance]:
        pass

    @abstractmethod
    def sync_transactions(
        self, sync_cursor: Optional[SyncCursor], access_token: Optional[str]
    ) -> SyncTransactionsResponse:
        pass
