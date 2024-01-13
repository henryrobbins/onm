import os
from enum import Enum
from typing import Dict
from configparser import ConfigParser

from onm.source.source import Source
from onm.source.plaid_source import PlaidSource


class SourceType(Enum):
    PLAID="plaid"


SOURCE_TYPE = "type"
ACCESS_TOKEN = "access_token"


# TODO: Check more than one place for config file
ONM_SOURCES_PATH = os.path.expanduser("~/.config/onm/sources.ini")

class Sources:

    def __init__(self, sources_path: str = None):
        self.config_path = sources_path or ONM_SOURCES_PATH
        self.config = ConfigParser(comment_prefixes=';', allow_no_value=True)
        self.config.read(self.config_path)

    def add_source(self, source: Source):
        if type(source) == PlaidSource:
            self._add_plaid_source(source)
        else:
            ValueError("Unsupported source")
        self._update()

    def _add_plaid_source(self, source: PlaidSource):
        self.config[source.name] = {}
        config_source = self.config[source.name]
        config_source[SOURCE_TYPE] = SourceType.PLAID.value
        config_source[ACCESS_TOKEN] = source.access_token
        for account_id, account_name in source.account_id_map.items():
            config_source[account_id] = account_name

    def get_source(self, name: str) -> Source:
        if not self.config.has_section(name):
            raise ValueError(f"Source '{name}' does not exist")
        source = self.config[name]
        source_type = SourceType(source[SOURCE_TYPE])
        if source_type == SourceType.PLAID:
            return self._get_plaid_source(name, source)

    def _get_plaid_source(self, name: str, source: Dict) -> PlaidSource:
        account_id_map = {}
        for k, v in source.items():
            if k not in ("name", "access_token"):
                account_id_map[k] = v
        return PlaidSource(
            name=name,
            access_token=source[ACCESS_TOKEN],
            account_id_map=account_id_map
        )

    def _update(self):
        with open(self.config_path, "w+") as f:
            self.config.write(f)
