import os
from configparser import ConfigParser, NoSectionError
from .database.database import Database, DatabaseType
from .database.database_factory import DatabaseFactory
from .connection.plaid_connection import PlaidConfiguration
import pkg_resources

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = os.path.expanduser("~/.config/onm/config.ini")

ONM_SECTION = "onm"
DATABASE_TYPE = "db_type"

DATABASE_SECTION = "database"

PLAID_SECTION = "Plaid"
PLAID_CLIENT_ID = "client_id"
PLAID_SECRET = "secret"
PLAID_ENV = "environment"


DEFAULT_CONFIG_PATH = pkg_resources.resource_filename(__name__, "data/config.ini")
DEFAULT_CONFIG = ConfigParser(comment_prefixes=";", allow_no_value=True)
DEFAULT_CONFIG.read(DEFAULT_CONFIG_PATH)


class Config:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or ONM_CONFIG_PATH
        self.config = ConfigParser(comment_prefixes=";", allow_no_value=True)
        self.config.read(self.config_path)

    def get_plaid_config(self) -> PlaidConfiguration:
        if not self.config.has_section(PLAID_SECTION):
            raise ValueError(f"Configuration file is missing [{PLAID_SECTION}] section")
        return PlaidConfiguration(
            client_id=self.config[PLAID_SECTION][PLAID_CLIENT_ID],
            secret=self.config[PLAID_SECTION][PLAID_SECRET],
            environment=self.config[PLAID_SECTION][PLAID_ENV],
        )

    def get_database(self) -> Database:
        try:
            database_type = DatabaseType(self.config[ONM_SECTION][DATABASE_TYPE])
            kwargs = self.config[DATABASE_SECTION]
        except (NoSectionError, KeyError):
            # TODO: some warning falling back (maybe in verbose mode)
            database_type = DatabaseType(DEFAULT_CONFIG[ONM_SECTION][DATABASE_TYPE])
            kwargs = DEFAULT_CONFIG[DATABASE_SECTION]
        return DatabaseFactory.create_database(database_type, **kwargs)

    def update(self):
        with open(self.config_path, "w+") as f:
            self.config.write(f)
