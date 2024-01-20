from ..common import SourceType
from onm.config import Config
from .connection import Connection
from .plaid_connection import PlaidConnection
from onm.connection.csv_connection import AppleCsvConnection, AmexCsvConnection
from onm.connection.plaid_connection import get_plaid_api
from typing import Optional


class ConnectionFactory:
    @staticmethod
    def create_connection(
        type: SourceType,
        config: Config,
        csv_path: Optional[str] = None,  # TODO: do I really want this here?
    ) -> Connection:
        if type == SourceType.PLAID:
            plaid_config = config.get_plaid_config()
            plaid_api = get_plaid_api(plaid_config)
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
