from ..common import SourceType
from .link import Link
from .plaid_link import PlaidLink
from plaid.api.plaid_api import PlaidApi
from typing import Optional


class LinkFactory():

    @staticmethod
    def create_link(type: SourceType, plaid_api: Optional[PlaidApi]) -> Link:
        if type == SourceType.PLAID:
            if plaid_api is None:
                raise ValueError("Must provide 'plaid_api' for plaid link")
            return PlaidLink(plaid_api)
        else:
            raise ValueError("Unknown type")