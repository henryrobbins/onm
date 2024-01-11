# https://github.com/henryrobbins/plaid-sync/blob/update-plaid/plaidsync/plaidapi.py
# https://github.com/mbafford/plaid-sync/blob/master/plaidapi.py

import re
import json
import datetime

import plaid
from plaid import Configuration
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.item_get_response import ItemGetResponse
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.accounts_get_response import AccountsGetResponse
from plaid.model.account_base import AccountBase
from plaid.model import transaction
from plaid.model.personal_finance_category import PersonalFinanceCategory
from .transaction import Transaction, TransactionType
from .account import Account
from .importer import Source
from plaid.model.item import Item
from typing import Optional, List, Dict


class AccountBalance:
    def __init__(self, data: AccountBase):
        self.raw_data = serialize_account_base(data)
        self.account_id        = data.account_id
        self.account_name      = data.name
        self.account_type      = str(data.type)
        self.account_subtype   = str(data.subtype)
        self.account_number    = data.mask
        self.balance_current   = data.balances.current
        self.balance_available = data.balances.available
        self.balance_limit     = data.balances.limit
        self.currency_code     = data.balances.iso_currency_code


class AccountInfo:
    def __init__(self, data: ItemGetResponse):
        self.raw_data = serialize_item(data.item)
        self.item_id                   = data.item.item_id
        self.institution_id            = data.item.institution_id
        self.ts_consent_expiration     = data.item.consent_expiration_time
        self.ts_last_failed_update     = data.status.transactions.last_failed_update
        self.ts_last_successful_update = data.status.transactions.last_successful_update


# class Transaction:
#     def __init__(self, data: plaid.model.transaction.Transaction):
#         self.raw_data = serialize_transaction(data)
#         self.account_id     = data.account_id
#         self.date           = data.date
#         self.transaction_id = data.transaction_id
#         self.pending        = data.pending
#         self.merchant_name  = data.merchant_name
#         self.amount         = data.amount
#         self.currency_code  = data.iso_currency_code

#     def __str__(self):
#         return "%s %s %s - %4.2f %s" % ( self.date, self.transaction_id, self.merchant_name, self.amount, self.currency_code )


def raise_plaid(ex: plaid.ApiException):
    response = json.loads(ex.body)
    if response['error_code'] == 'NO_ACCOUNTS':
        raise PlaidNoApplicableAccounts(response)
    elif response['error_code'] == 'ITEM_LOGIN_REQUIRED':
        raise PlaidAccountUpdateNeeded(response)
    else:
        raise PlaidUnknownError(response)


class PlaidError(Exception):
    def __init__(self, plaid_error):
        super().__init__()
        self.error_code = plaid_error["error_code"]
        self.error_message = plaid_error["error_message"]

    def __str__(self):
        return "%s: %s" % (self.error_code, self.error_message)


class PlaidUnknownError(PlaidError):
    pass


class PlaidNoApplicableAccounts(PlaidError):
    pass


class PlaidAccountUpdateNeeded(PlaidError):
    pass


class PlaidConfiguration():

    def __init__(self, client_id: str, secret: str, environment: str):
        self._client_id = client_id
        self._secret = secret
        self._environment = environment

    @property
    def client_id(self) -> str:
        return self._client_id

    @client_id.setter
    def client_id(self, client_id: str):
        self._client_id = client_id

    @property
    def secret(self) -> str:
        return self._secret

    @secret.setter
    def secret(self, secret: str):
        self._secret = secret

    @property
    def environment(self) -> str:
        return self._environment

    @environment.setter
    def environment(self, environment: str):
        self._environment = environment


class PlaidAPI():

    def __init__(self, configuration: PlaidConfiguration):
        config = Configuration(
            host=get_host(configuration.environment),
            api_key={
                'clientId': configuration.client_id,
                'secret': configuration.secret
            }
        )
        api_client = plaid.ApiClient(config)
        self.client = plaid_api.PlaidApi(api_client)

    def get_link_token(self, access_token=None) -> str:
        """
        Return link token to create a link or update an existing one.

        https://plaid.com/docs/api/tokens/#token-exchange-flow
        """

        data = {
            'user': {
                'client_user_id': 'abc123',
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
        res = self.client.link_token_create(req)
        return res.link_token

    def exchange_public_token(self, public_token: str) -> str:
        """
        Exchange a temporary public token for a permanent private access token.
        """
        req = ItemPublicTokenExchangeRequest(public_token)
        res = self.client.item_public_token_exchange(req)
        return res.access_token


    def get_account_balance(self, access_token: str) -> Dict[AccountBalance, float]:
        """
        Returns the balances of all accounts associated with this particular access_token.
        """
        req = AccountsBalanceGetRequest(access_token=access_token)
        res = self.client.accounts_balance_get(req)
        plaid_accounts = res.accounts

        account_balance_dict = {}
        for plaid_account in plaid_accounts:
            account = Account(
                account_name=plaid_account.official_name or plaid_account.name,
                source=Source.PLAID,
                access_token=access_token,
                account_id=plaid_account.account_id
            )
            # TODO: Use current for now but should do based on account type
            balance = plaid_account.balances.current
            account_balance_dict[account] = balance

        return account_balance_dict

    def get_transactions(self, account: Account):
        transactions = []
        has_more = True
        next_cursor = ""
        while has_more:
            req = TransactionsSyncRequest(
                access_token=account.access_token,
                cursor=next_cursor
            )
            res = self.client.transactions_sync(req)
            has_more = res.has_more
            next_cursor = res.next_cursor
            added = res.added
            filtered = [t for t in added if t.account_id == account.account_id]
            transactions += [parse_plaid_transaction(account.account_name, t) for t in filtered]
        return transactions


def parse_plaid_transaction(account_name: str, transaction: transaction.Transaction) -> Transaction:
    amount = transaction.amount
    type = TransactionType.DEBIT if amount < 0 else TransactionType.CREDIT
    amount = abs(amount)
    return Transaction(
        date=transaction.date,
        description=transaction.name,
        amount=amount,
        type=type,
        category=parse_plaid_category(transaction.personal_finance_category),
        account=account_name
    )


def parse_plaid_category(plaid_category: PersonalFinanceCategory) -> str:
    return f"{plaid_category.primary}:{plaid_category.detailed}"


def get_host(env: str) -> str:
    if env == "sandbox":
        return plaid.Environment.Sandbox
    elif env == "development":
        return plaid.Environment.Development
    elif env == "production":
        return plaid.Environment.Production
    else:
        raise ValueError("{env} is not a valid environment")

