from datetime import date
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, NamedTuple


class AccountBalance(NamedTuple):
    account_name: str
    account_id: str
    balance: float


class AccountBalancesResponse(NamedTuple):
    accounts: List[AccountBalance]


class TransactionType(Enum):
    CREDIT= "credit"
    DEBIT= "debit"


class Transaction(NamedTuple):
    date: date
    description: str
    amount: float
    category: str
    account_id: str
    type: TransactionType


class NewTransactionsResponse(NamedTuple):
    transactions: List[Transaction]


class Connection(ABC):

    @abstractmethod
    def get_account_balances(self) -> AccountBalancesResponse:
        pass

    @abstractmethod
    def get_new_transactions(self) -> NewTransactionsResponse:
        pass

