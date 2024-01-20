import os
import tomlkit
from .database.database import DatabaseType, DatabaseConfiguration
from .connection.plaid_connection import PlaidConfiguration
import pkg_resources

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = os.path.expanduser("~/.config/onm/config.toml")

ONM_SECTION = "onm"
DATABASE_TYPE = "database_type"

DATABASE_SECTION = "database"

PLAID_SECTION = "plaid"
PLAID_CLIENT_ID = "client_id"
PLAID_SECRET = "secret"
PLAID_ENV = "environment"


DEFAULT_CONFIG_PATH = pkg_resources.resource_filename(__name__, "data/config.toml")
DEFAULT_CONFIG = tomlkit.TOMLDocument()
with open(DEFAULT_CONFIG_PATH, mode="rt", encoding="utf-8") as fp:
    DEFAULT_CONFIG = tomlkit.load(fp)


class Config:
    def __init__(self, config_path: str = None):
        self._config_path = config_path or ONM_CONFIG_PATH
        with open(self._config_path, mode="rt", encoding="utf-8") as fp:
            self._config = tomlkit.load(fp)

    def get_plaid_config(self) -> PlaidConfiguration:
        # TODO: error handling
        return PlaidConfiguration(
            client_id=self._config[PLAID_SECTION][PLAID_CLIENT_ID],
            secret=self._config[PLAID_SECTION][PLAID_SECRET],
            environment=self._config[PLAID_SECTION][PLAID_ENV],
        )

    def get_database_config(self) -> DatabaseConfiguration:
        # TODO: error handling
        database_type = DatabaseType(self._config[ONM_SECTION][DATABASE_TYPE])
        parameters = self._config[DATABASE_SECTION]
        return DatabaseConfiguration(type=database_type, parameters=parameters)
