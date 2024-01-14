from .source import Source
from .plaid_source import PlaidSourceBuilder
from ..common import SourceType
from ..link.link_factory import LinkFactory
from ..connection.connection_factory import ConnectionFactory
from plaid.api.plaid_api import PlaidApi
from typing import Type, Optional


class SourceFactory():

    def create_source(type: SourceType, name: str,
                      link_factory: Type[LinkFactory] = LinkFactory,
                      connection_factory: Type[ConnectionFactory] = ConnectionFactory,
                      plaid_api: Optional[PlaidApi] = None) -> Source:
        link = link_factory.create_link(type, plaid_api=plaid_api)
        access_token = link.get_access_token()
        connection = connection_factory.create_connection(type, plaid_api=plaid_api)

        if type == SourceType.PLAID:
            return PlaidSourceBuilder.build(name, access_token, connection)
        else:
            raise ValueError("Unknown type")

