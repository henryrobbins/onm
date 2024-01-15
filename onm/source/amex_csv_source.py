from plaid.api.plaid_api import PlaidApi
from onm.common import Account, Transaction, TransactionType
from onm.link.link_factory import LinkFactory
from onm.sync import SyncCursor
from onm.connection import connection
from onm.connection.amex_csv_connection import AmexCsvConnection
from .source import Source, SyncTransactionsResponse, SourceType
from typing import List, Optional, Type


class AmexCsvSource(Source):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def type(self) -> str:
        return SourceType.AMEX_CSV

    def get_account_balances(self, connection: AmexCsvConnection) -> List[Account]:
        balances = connection.get_account_balances()
        accounts = []
        for b in balances:
            accounts.append(Account(name=self._name, balance=b.balance))
        return accounts

    def sync_transactions(
        self, connection: AmexCsvConnection, sync_cursor: Optional[SyncCursor]
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

    def update_link(
        self,
        link_factory: Type[LinkFactory] = LinkFactory,
        plaid_api: Optional[PlaidApi] = None,
    ) -> None:
        return super().update_link()
