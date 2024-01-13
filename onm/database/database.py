from abc import ABC, abstractmethod
from ..common import Account, Transaction
from typing import List


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
