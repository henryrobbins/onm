from enum import Enum
from datetime import date
from .importer import Source, CSV
from typing import Optional


class Account:

    def __init__(self, account_name: str, last_updated: Optional[date] = None,
                 source: Optional[Source] = None, csv_type: Optional[CSV] = None,
                 access_token: Optional[str] = None, account_id: Optional[str] = None):
        self._account_name = account_name
        self._last_updated = last_updated
        self._source = source
        self._csv_type = csv_type
        self._access_token = access_token
        self._account_id = account_id

    @property
    def account_name(self):
        return self._account_name

    @account_name.setter
    def account_name(self, account_name: str):
        self._account_name = account_name

    @property
    def last_updated(self):
        return self._last_updated

    @last_updated.setter
    def last_updated(self, date: Optional[date]):
        self._last_updated = date

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source: Optional[Source]):
        self._source = source

    @property
    def csv_type(self):
        return self._csv_type

    @csv_type.setter
    def csv_type(self, csv_type: Optional[CSV]):
        self._csv_type = csv_type

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token: Optional[str]):
        self._access_token = access_token

    @property
    def account_id(self):
        return self._account_id

    @account_id.setter
    def account_id(self, account_id: Optional[str]):
        self._account_id = account_id
