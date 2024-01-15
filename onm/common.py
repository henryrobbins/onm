from datetime import date
from enum import Enum
from typing import NamedTuple


class SourceType(Enum):
    PLAID="plaid"
    AMEX_CSV="amex_csv"

class Account(NamedTuple):
    name: str
    balance: float


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
