from ..common import SourceType
from .link import Link
from .plaid_link import PlaidLink
from onm.connection.plaid_connection import get_plaid_api
from onm.config import Config


class LinkFactory:
    @staticmethod
    def create_link(type: SourceType, config: Config) -> Link:
        if type == SourceType.PLAID:
            plaid_config = config.get_plaid_config()
            plaid_api = get_plaid_api(plaid_config)
            return PlaidLink(plaid_api)
        else:
            raise ValueError("Unknown type")
