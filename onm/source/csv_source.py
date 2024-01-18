from abc import ABC
from onm.common import Account, Transaction, TransactionType
from onm.category import (
    APPLE_ONM_CATEGORY_MAPPING,
    AMEX_ONM_CATEGORY_MAPPING,
    get_onm_category,
)
from onm.sync import SyncCursor
from onm.connection import connection
from onm.connection.connection import Connection
from onm.source.source import SourceType, Source, SyncTransactionsResponse
from typing import Dict, List, Optional


class CsvSource(Source, ABC):
    def __init__(self, name: str, category_mapping: Dict[str, str]):
        super().__init__(name)
        self._category_mapping = category_mapping

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
            category=get_onm_category(
                t.primary_category, t.detailed_category, self._category_mapping
            ),
            type=TransactionType(t.type.value),
        )


class AppleCsvSource(CsvSource):
    def __init__(self, name: str):
        super().__init__(name, APPLE_ONM_CATEGORY_MAPPING)

    @property
    def type(self) -> str:
        return SourceType.APPLE_CSV


class AmexCsvSource(CsvSource):
    def __init__(self, name: str):
        super().__init__(name, AMEX_ONM_CATEGORY_MAPPING)

    @property
    def type(self) -> str:
        return SourceType.AMEX_CSV
