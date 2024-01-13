from .source.source import Source
from typing import Optional


class Account:

    def __init__(self, account_name: str, source: Optional[Source] = None,
                 account_id: Optional[str] = None):
        self._account_name = account_name
        self._source = source
        self._account_id = account_id

    @property
    def account_name(self):
        return self._account_name

    @account_name.setter
    def account_name(self, account_name: str):
        self._account_name = account_name

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source: Optional[Source]):
        self._source = source

    @property
    def account_id(self):
        return self._account_id

    @account_id.setter
    def account_id(self, account_id: Optional[str]):
        self._account_id = account_id
