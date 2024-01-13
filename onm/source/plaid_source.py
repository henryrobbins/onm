from onm.source.source import Transaction, TransactionType
from ..connection import connection
from ..connection.plaid_connection import PlaidConnection
from .source import Source, SourceFactory
from typing import List, Dict


class PlaidSource(Source):

    def __init__(self, name: str, access_token: str = None,
                 account_id_map: Dict[str, str] = None):
        super().__init__(name)
        self._access_token = access_token
        self._account_id_map = account_id_map

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def account_id_map(self) -> str:
        return self._account_id_map

    def get_account_balances(self, plaid_connection: PlaidConnection) -> Dict[str, float]:
        balances = plaid_connection.get_account_balances(self._access_token)
        return {self._account_id_map[b.account_id]: b.balance for b in balances}

    def get_new_transactions(self, plaid_connection: PlaidConnection) -> List[Transaction]:
        transactions = plaid_connection.get_new_transactions(self._access_token)
        return [self._transaction_from(t) for t in transactions]

    def _transaction_from(self, t: connection.Transaction) -> Transaction:
        return Transaction(
            date=t.date,
            description=t.description,
            amount=t.amount,
            account_name=self._account_id_map[t.account_id],
            category=t.category,
            type=TransactionType(t.type.value)
        )

class PlaidSourceFactory(SourceFactory):

    def create_source(name: str, access_token: str, plaid_connection: PlaidConnection) -> PlaidSource:
        accounts = plaid_connection.get_account_balances(access_token)
        account_id_map = {a.account_id: a.account_name for a in accounts}

        # TODO: custom naming logic
        # account_names = {a.account_name: a for a in account_balances.keys()}
        # selected_accounts = _editor_account_selection(list(account_names.keys()))

        # selected_account_balances = {}
        # for current_name, rename in selected_accounts.items():
        #     account = account_names[current_name]
        #     balance = account_balances[account]
        #     account.account_name = rename
        #     selected_account_balances[account] = balance

        return PlaidSource(
            name=name,
            access_token=access_token,
            account_id_map=account_id_map
        )
