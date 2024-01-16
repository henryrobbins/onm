import os
import tomlkit
from typing import Dict

from onm.common import SourceType
from onm.source.source import Source
from onm.source.plaid_source import PlaidSource
from onm.source.csv_source import AppleCsvSource, AmexCsvSource


SOURCE_TYPE = "type"
ACCESS_TOKEN = "access_token"
ACCOUNT_ID_MAP = "account_id_map"


# TODO: Check more than one place for config file
ONM_SOURCES_PATH = os.path.expanduser("~/.config/onm/sources.toml")


class Sources:
    def __init__(self, sources_path: str = None):
        self.config_path = sources_path or ONM_SOURCES_PATH
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as _:
                pass
        with open(self.config_path, mode="rt", encoding="utf-8") as fp:
            config = tomlkit.load(fp)
        self._config = config

    def add_source(self, source: Source):
        if source.type == SourceType.PLAID:
            self._add_plaid_source(source)
        elif source.type == SourceType.AMEX_CSV:
            self._add_csv_source(source)
        elif source.type == SourceType.APPLE_CSV:
            self._add_csv_source(source)
        else:
            raise ValueError("Unsupported source")
        self._update()

    def _add_plaid_source(self, source: PlaidSource):
        source_config = tomlkit.table()
        source_config.add(SOURCE_TYPE, source.type.value)
        source_config.add(ACCESS_TOKEN, source.access_token)
        accounts = tomlkit.array()
        ts = []
        for account_id, account_name in source.account_id_map.items():
            t = tomlkit.inline_table()
            t.add("id", account_id)
            t.add("name", account_name)
            ts.append(t)
        accounts.extend(ts)
        source_config.add(ACCOUNT_ID_MAP, accounts.multiline(True))
        self._config.add(source.name, source_config)

    def _add_csv_source(self, source: Source):
        source_config = tomlkit.table()
        source_config.add(SOURCE_TYPE, source.type.value)
        self._config.add(source.name, source_config)

    def get_source(self, name: str) -> Source:
        # if not self._config.has_section(name):
        #     raise ValueError(f"Source '{name}' does not exist")
        source_config = self._config.get(name)
        source_type = SourceType(source_config.get(SOURCE_TYPE))
        if source_type == SourceType.PLAID:
            return self._get_plaid_source(name, source_config)
        elif source_type == SourceType.AMEX_CSV:
            return AmexCsvSource(name)
        elif source_type == SourceType.APPLE_CSV:
            return AppleCsvSource(name)
        else:
            raise ValueError("Unsupported source")

    def _get_plaid_source(self, name: str, source_config: Dict) -> PlaidSource:
        account_id_map = {}
        for account in source_config.get(ACCOUNT_ID_MAP):
            account_id_map[account.get("id")] = account.get("name")
        return PlaidSource(
            name=name,
            access_token=source_config.get(ACCESS_TOKEN),
            account_id_map=account_id_map,
        )

    def _update(self):
        with open(self.config_path, mode="wt", encoding="utf-8") as fp:
            tomlkit.dump(self._config, fp)
