from plaid import ApiClient, Configuration, Environment
from plaid.model import transaction
from plaid.api.plaid_api import PlaidApi
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.personal_finance_category import PersonalFinanceCategory
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from .. import webserver
from .connection import (Connection, AccountBalance,
                         TransactionType, Transaction, SyncTransactionsResponse)
from ..sync import PlaidSyncCursor
from typing import List, NamedTuple, Optional


class PlaidConfiguration(NamedTuple):
    client_id: str
    secret: str
    environment: str


def _get_host(env: str) -> str:
    if env == "sandbox":
        return Environment.Sandbox
    elif env == "development":
        return Environment.Development
    elif env == "production":
        return Environment.Production
    else:
        raise ValueError("{env} is not a valid environment")


def get_plaid_api(plaid_config: PlaidConfiguration) -> PlaidApi:
    config = Configuration(
        host=_get_host(plaid_config.environment),
        api_key={
            'clientId': plaid_config.client_id,
            'secret': plaid_config.secret
        }
    )
    api_client = ApiClient(config)
    return PlaidApi(api_client)


class PlaidLink():

    def __init__(self, plaid_api : PlaidApi):
        self._plaid_api = plaid_api

    def get_access_token(self):
        link_token = self._get_link_token()
        public_token = self._get_public_token(link_token)
        access_token = self._exchange_public_token(public_token)
        return access_token

    def update_link(self, access_token: str):
        link_token = self._get_link_token(access_token)
        webserver.serve(
            clientName="onm",
            pageTitle="Update Account Credentials",
            type="update",
            token=link_token
        )

    def _get_link_token(self, access_token: str = None) -> str:
        data = {
            'user': {
                'client_user_id': 'onm',
            },
            'client_name': 'onm',
            'country_codes': [CountryCode('US')],
            'language': 'en',
        }
        if access_token:
            data['access_token'] = access_token
        else:
            data['products'] = [Products('transactions')]
        req = LinkTokenCreateRequest(**data)
        res = self._plaid_api.link_token_create(req)
        return res.link_token

    def _get_public_token(self, link_token: str = None) -> str:
        plaid_response = webserver.serve(
            clientName="onm",
            pageTitle="Link Account Credentials",
            type="link",
            token=link_token
        )
        return plaid_response['public_token']

    def _exchange_public_token(self, public_token: str) -> str:
        req = ItemPublicTokenExchangeRequest(public_token)
        res = self._plaid_api.item_public_token_exchange(req)
        return res.access_token


class PlaidConnection(Connection):

    def __init__(self, plaid_api: PlaidApi):
        self._plaid_api = plaid_api

    def get_account_balances(self, access_token: Optional[str]) -> List[AccountBalance]:
        req = AccountsBalanceGetRequest(access_token=access_token)
        res = self._plaid_api.accounts_balance_get(req)
        plaid_accounts = res.accounts
        accounts = []
        for plaid_account in plaid_accounts:
            accounts.append(AccountBalance(
                account_name = plaid_account.official_name or plaid_account.name,
                account_id = plaid_account.account_id,
                # TODO: Use current for now but should do based on account type
                balance = plaid_account.balances.current
            ))
        return accounts

    def sync_transactions(self, sync_cursor: Optional[PlaidSyncCursor] = None,
                          access_token: Optional[str] = None) -> SyncTransactionsResponse:
        transactions = []
        has_more = True
        next_cursor = ""
        if sync_cursor is not None and sync_cursor.cursor is not None:
            next_cursor = sync_cursor.cursor
        while has_more:
            req = TransactionsSyncRequest(
                access_token=access_token,
                cursor=next_cursor
            )
            res = self._plaid_api.transactions_sync(req)
            has_more = res.has_more
            next_cursor = res.next_cursor
            transactions += [_parse_plaid_transaction(t) for t in res.added]
        return SyncTransactionsResponse(
            transactions=transactions,
            sync_cursor=PlaidSyncCursor(cursor=next_cursor)
        )


def _parse_plaid_transaction(transaction: transaction.Transaction) -> Transaction:
    amount = transaction.amount
    type = TransactionType.DEBIT if amount < 0 else TransactionType.CREDIT
    amount = abs(amount)
    return Transaction(
        date=transaction.date,
        description=transaction.name,
        amount=amount,
        type=type,
        category=_parse_plaid_category(transaction.personal_finance_category),
        account_id=transaction.account_id
    )


def _parse_plaid_category(plaid_category: PersonalFinanceCategory) -> str:
    return f"{plaid_category.primary}:{plaid_category.detailed}"
