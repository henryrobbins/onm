from ..common import SourceType
from .connection import Connection
from .plaid_connection import PlaidConnection
from plaid.api.plaid_api import PlaidApi
from typing import Optional


class ConnectionFactory():

    @staticmethod
    def create_connection(type: SourceType, plaid_api: Optional[PlaidApi]) -> Connection:
        if type == SourceType.PLAID:
            if plaid_api is None:
                raise ValueError("Must provide 'plaid_api' for plaid link")
            return PlaidConnection(plaid_api)
        else:
            raise ValueError("Unknown type")
