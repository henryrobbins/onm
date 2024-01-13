from datetime import date
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, NamedTuple


class TransactionType(Enum):
    CREDIT= "credit"
    DEBIT= "debit"


class Transaction(NamedTuple):
    date: date
    description: str
    amount: float
    category: str
    account_name: str
    type: TransactionType


class Source(ABC):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_account_balances(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def get_new_transactions(self) -> List[Transaction]:
        pass


class SourceFactory(ABC):

    @abstractmethod
    def create_source(self) -> Source:
        pass
