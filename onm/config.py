import os
from .importer import Source, CSV
from .account import Account
from configparser import ConfigParser
from datetime import datetime, date
from .source.plaid_source import PlaidConfiguration
import pkg_resources
from typing import Optional

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = os.path.expanduser("~/.config/onm/config.ini")

ONM_SECTION = "onm"
TRANSACTIONS = "transactions"

LAST_UPDATED = "last_updated"
SOURCE = "source"
CSV_TYPE = "csv_type"
ACCESS_TOKEN = "access_token"
ACCOUNT_ID = "account_id"

PLAID_SECTION = "Plaid"
PLAID_CLIENT_ID = "client_id"
PLAID_SECRET = "secret"
PLAID_ENV = "environment"

DATE_FMT = r"%Y-%m-%d"

DEFAULT_CONFIG_PATH = pkg_resources.resource_filename(__name__, "data/config.ini")
DEFAULT_CONFIG = ConfigParser(comment_prefixes=';', allow_no_value=True)
DEFAULT_CONFIG.read(DEFAULT_CONFIG_PATH)

class Config:

    def __init__(self, config_path: str = None):
        self.config_path = config_path or ONM_CONFIG_PATH
        self.config = ConfigParser(comment_prefixes=';', allow_no_value=True)
        self.config.read(self.config_path)

    @property
    def transactions(self) -> str:
        path = self.config[ONM_SECTION].get(
            TRANSACTIONS, DEFAULT_CONFIG[ONM_SECTION][TRANSACTIONS])
        path = os.path.expanduser(path)
        return path

    def get_account(self, account_name: str) -> Account:
        if not self.config.has_section(account_name):
            raise ValueError(f"{account_name} does not exist")
        account = self.config[account_name]
        return Account(
            account_name=account_name,
            last_updated=_deserialize_date(account.get(LAST_UPDATED, "none")),
            source=_deserialize_source(account.get(SOURCE, "none")),
            csv_type=_deserialize_csv_type(account.get(CSV_TYPE, "none")),
            access_token=account.get(ACCESS_TOKEN, None),
            account_id=account.get(ACCOUNT_ID, None)
        )

    def update_account(self, account: Account):
        name = account.account_name
        if not self.config.has_section(name):
            self.config[name] = {}
        if account.last_updated is not None:
            self.config[name][LAST_UPDATED] = _serialize_date(account.last_updated)
        if account.source is not None:
            self.config[name][SOURCE] = account.source.value
        if account.csv_type is not None:
            self.config[name][CSV_TYPE] = account.csv_type.value
        if account.access_token is not None:
            self.config[name][ACCESS_TOKEN] = account.access_token
        if account.account_id is not None:
            self.config[name][ACCOUNT_ID] = account.account_id
        self.update()

    def get_plaid_config(self) -> PlaidConfiguration:
        if not self.config.has_section(PLAID_SECTION):
            raise ValueError(f"Configuration file is missing [{PLAID_SECTION}] section")
        return PlaidConfiguration(
            client_id=self.config[PLAID_SECTION][PLAID_CLIENT_ID],
            secret=self.config[PLAID_SECTION][PLAID_SECRET],
            environment=self.config[PLAID_SECTION][PLAID_ENV]
        )

    def update(self):
        with open(self.config_path, "w+") as f:
            self.config.write(f)


def _serialize_date(date: Optional[date]) -> str:
    return datetime.strftime(date, DATE_FMT)


def _deserialize_date(date_str: str) -> Optional[date]:
    if date_str == "none":
        return None
    try:
        return datetime.strptime(date_str, DATE_FMT).date()
    except KeyError:
        raise ValueError(f"'{date_str}' is not in the date format: {DATE_FMT}")


def _deserialize_source(source_str: str) -> Optional[Source]:
    if source_str == "none":
        return None
    try:
        return Source(source_str)
    except KeyError:
        raise ValueError(f"'{source_str}' is not a supported import source")


def _deserialize_csv_type(csy_type_str: str) -> Optional[CSV]:
    if csy_type_str == "none":
        return None
    try:
        return CSV(csy_type_str)
    except KeyError:
        raise ValueError(f"'{csy_type_str}' is not a supported CSV type")
