from onm.source.apple_csv_source import AppleCsvSource
from .source import Source
from .plaid_source import PlaidSourceBuilder
from .amex_csv_source import AmexCsvSource
from ..common import SourceType
from ..link.link_factory import LinkFactory
from ..connection.connection_factory import ConnectionFactory
from plaid.api.plaid_api import PlaidApi
from typing import Type, Optional


class SourceFactory:
    @staticmethod
    def create_source(
        type: SourceType,
        name: str,
        link_factory: Type[LinkFactory] = LinkFactory,
        connection_factory: Type[ConnectionFactory] = ConnectionFactory,
        plaid_api: Optional[PlaidApi] = None,
        csv_type: Optional[str] = None,
    ) -> Source:
        if type == SourceType.PLAID:
            link = link_factory.create_link(type, plaid_api=plaid_api)
            access_token = link.get_access_token()
            connection = connection_factory.create_connection(type, plaid_api=plaid_api)
            return PlaidSourceBuilder.build(name, access_token, connection)
        elif type == SourceType.AMEX_CSV:
            return AmexCsvSource(name)
        elif type == SourceType.APPLE_CSV:
            return AppleCsvSource(name)
        else:
            raise ValueError("Unknown type")
