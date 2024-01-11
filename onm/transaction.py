import pandas as pd
from datetime import date
from typing import List


class TransactionType:
    CREDIT = "credit"
    DEBIT = "debit"


class Transaction:

    def __init__(self, date: date, description: str, category: str, amount: float, type: TransactionType, account: str):
        self._date = date
        self._description = description
        self._category = category
        self._amount = amount
        self._type = type
        self._account = account

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = category

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        self._amount = amount

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, account):
        self._account = account


def transaction_table(transactions: List[Transaction]) -> pd.DataFrame:
    return pd.DataFrame([t.__dict__ for t in transactions])
