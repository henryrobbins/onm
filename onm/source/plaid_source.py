from onm.common import Account, Transaction, TransactionType, SourceType
from onm.link.link_factory import LinkFactory
from ..connection import connection
from onm.config import Config
from ..connection.plaid_connection import PlaidConnection
from ..sync import PlaidSyncCursor
from .source import Source, SyncTransactionsResponse
from typing import List, Dict


class PlaidSource(Source):
    def __init__(
        self, name: str, access_token: str = None, account_id_map: Dict[str, str] = None
    ):
        super().__init__(name)
        self._access_token = access_token
        self._account_id_map = account_id_map

    @property
    def type(self) -> str:
        return SourceType.PLAID

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def account_id_map(self) -> str:
        return self._account_id_map

    def get_account_balances(self, connection: PlaidConnection) -> List[Account]:
        balances = connection.get_account_balances(self._access_token)
        accounts = []
        for b in balances:
            accounts.append(
                Account(name=self._account_id_map[b.account_id], balance=b.balance)
            )
        return accounts

    def sync_transactions(
        self, connection: PlaidConnection, sync_cursor: PlaidSyncCursor = None
    ) -> SyncTransactionsResponse:
        sync_response = connection.sync_transactions(
            sync_cursor=sync_cursor, access_token=self._access_token
        )
        transactions = [self._transaction_from(t) for t in sync_response.transactions]
        return SyncTransactionsResponse(
            transactions=transactions, sync_cursor=sync_response.sync_cursor
        )

    def _transaction_from(self, t: connection.Transaction) -> Transaction:
        return Transaction(
            date=t.date,
            description=t.description,
            amount=t.amount,
            account_name=self._account_id_map[t.account_id],
            category=self._onm_category_from_plaid(
                t.primary_category, t.detailed_category
            ),
            type=TransactionType(t.type.value),
        )

    @staticmethod
    def _onm_category_from_plaid(primary: str, detailed: str) -> str:
        return f"{primary}:{detailed[len(primary) + 1: len(detailed)]}"

    def update_link(self, config: Config) -> None:
        link = LinkFactory.create_link(SourceType.PLAID, config)
        link.update_link(self.access_token)


class PlaidSourceBuilder:
    @staticmethod
    def build(
        name: str, access_token: str, plaid_connection: PlaidConnection
    ) -> PlaidSource:
        accounts = plaid_connection.get_account_balances(access_token)
        account_id_map = {a.account_id: a.account_name for a in accounts}

        # TODO: custom naming logic (UserInputHandler)
        # account_names = {a.account_name: a for a in account_balances.keys()}
        # selected_accounts = _editor_account_selection(list(account_names.keys()))

        # selected_account_balances = {}
        # for current_name, rename in selected_accounts.items():
        #     account = account_names[current_name]
        #     balance = account_balances[account]
        #     account.account_name = rename
        #     selected_account_balances[account] = balance

        return PlaidSource(
            name=name, access_token=access_token, account_id_map=account_id_map
        )
