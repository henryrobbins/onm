from __future__ import annotations
from onm.common import Account, Transaction, TransactionType, SourceType, AccountType
from onm.link.link_factory import LinkFactory
from ..connection import connection
from onm.config import Config
from ..connection.plaid_connection import PlaidConnection
from ..sync import PlaidSyncCursor
from .source import Source, SyncTransactionsResponse
from typing import List, Dict


class PlaidSource(Source):
    def __init__(
        self,
        name: str,
        access_token: str = None,
        account_map: Dict[str, Dict[str, str]] = None,
    ):
        super().__init__(name)
        self._access_token = access_token
        self._account_map = account_map

    @property
    def type(self) -> str:
        return SourceType.PLAID

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def account_map(self) -> str:
        return self._account_map

    def get_account_balances(self, connection: PlaidConnection) -> List[Account]:
        balances = connection.get_account_balances(self._access_token)
        accounts = []
        for b in balances:
            account_dict = self.account_map[b.account_id]
            accounts.append(
                Account(
                    name=account_dict["name"],
                    balance=b.balance,
                    type=AccountType(b.type.value),
                )
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
            account_name=self.account_map[t.account_id]["name"],
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

    def serialize(self) -> Dict:
        return {
            "type": SourceType.PLAID.value,
            "name": self.name,
            "access_token": self.access_token,
            "accounts": [
                {"id": k, "name": v["name"], "account_type": v["account_type"].value}
                for k, v in self.account_map.items()
            ],
        }

    @staticmethod
    def deserialize(data: Dict) -> PlaidSource:
        return PlaidSource(
            name=data["name"],
            access_token=data["access_token"],
            account_map={
                a["id"]: {
                    "name": a["name"],
                    "account_type": AccountType(a["account_type"]),
                }
                for a in data["accounts"]
            },
        )


class PlaidSourceBuilder:
    @staticmethod
    def build(
        name: str, access_token: str, plaid_connection: PlaidConnection
    ) -> PlaidSource:
        accounts = plaid_connection.get_account_balances(access_token)
        account_map = {
            a.account_id: {
                "name": a.account_name,
                "account_type": AccountType(a.type.value),
            }
            for a in accounts
        }

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
            name=name, access_token=access_token, account_map=account_map
        )
