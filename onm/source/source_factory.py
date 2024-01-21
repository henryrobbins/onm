from .source import Source
from .plaid_source import PlaidSource, PlaidSourceBuilder
from onm.source.csv_source import AppleCsvSource, AmexCsvSource
from ..common import SourceType
from onm.config import Config
from ..link.link_factory import LinkFactory
from ..connection.connection_factory import ConnectionFactory


class SourceFactory:
    @staticmethod
    def create_source(
        type: SourceType,
        name: str,
        config: Config,
    ) -> Source:
        if type == SourceType.PLAID:
            # TODO: error handling
            link = LinkFactory.create_link(type, config)
            access_token = link.get_access_token()
            connection = ConnectionFactory.create_connection(type, config)
            return PlaidSourceBuilder.build(name, access_token, connection)
        elif type == SourceType.AMEX_CSV:
            return AmexCsvSource(name)
        elif type == SourceType.APPLE_CSV:
            return AppleCsvSource(name)
        else:
            raise ValueError("Unknown type")

    @staticmethod
    def deserialize(data: dict) -> Source:
        type = SourceType(data.pop("type"))
        if type == SourceType.PLAID:
            return PlaidSource.deserialize(data)
        elif type == SourceType.AMEX_CSV:
            return AmexCsvSource.deserialize(data)
        elif type == SourceType.APPLE_CSV:
            return AppleCsvSource.deserialize(data)
        else:
            raise ValueError("Unknown type")
