from abc import ABC
from onm.common import Account, Transaction, TransactionType
from onm.sync import SyncCursor
from onm.connection import connection
from onm.connection.connection import Connection
from onm.source.source import SourceType, Source, SyncTransactionsResponse
from typing import List, Optional


class CsvSource(Source, ABC):
    def __init__(self, name: str):
        super().__init__(name)

    def get_account_balances(self, connection: Connection) -> List[Account]:
        balances = connection.get_account_balances()
        accounts = []
        for b in balances:
            accounts.append(Account(name=self._name, balance=b.balance))
        return accounts

    def sync_transactions(
        self, connection: Connection, sync_cursor: Optional[SyncCursor]
    ) -> SyncTransactionsResponse:
        sync_response = connection.sync_transactions(sync_cursor=sync_cursor)
        transactions = [self._transaction_from(t) for t in sync_response.transactions]
        return SyncTransactionsResponse(
            transactions=transactions, sync_cursor=sync_response.sync_cursor
        )

    def _transaction_from(self, t: connection.Transaction) -> Transaction:
        return Transaction(
            date=t.date,
            description=t.description,
            amount=t.amount,
            account_name=self._name,
            category=t.category,
            type=TransactionType(t.type.value),
        )


class AppleCsvSource(CsvSource):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def type(self) -> str:
        return SourceType.APPLE_CSV


class AmexCsvSource(CsvSource):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def type(self) -> str:
        return SourceType.AMEX_CSV
