from onm.connection.apple_csv_connection import AppleCsvConnection
from ..common import SourceType
from .connection import Connection
from .plaid_connection import PlaidConnection
from .amex_csv_connection import AmexCsvConnection
from plaid.api.plaid_api import PlaidApi
from typing import Optional


class ConnectionFactory:
    @staticmethod
    def create_connection(
        type: SourceType,
        plaid_api: Optional[PlaidApi] = None,
        csv_path: Optional[str] = None,
    ) -> Connection:
        if type == SourceType.PLAID:
            if plaid_api is None:
                raise ValueError("Must provide 'plaid_api' for plaid link")
            return PlaidConnection(plaid_api)
        elif type == SourceType.AMEX_CSV:
            if csv_path is None:
                raise ValueError("Must provide 'csv_path' for Amex CSV link")
            return AmexCsvConnection(csv_path)
        elif type == SourceType.APPLE_CSV:
            if csv_path is None:
                raise ValueError("Must provide 'csv_path' for Amex CSV link")
            return AppleCsvConnection(csv_path)
        else:
            raise ValueError("Unknown type")
