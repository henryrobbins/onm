import os
from configparser import ConfigParser
import pkg_resources

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = os.path.expanduser("~/.config/onm/config.ini")

ONM_SECTION = "onm"
TRANSACTIONS = "transactions"

DEFAULT_CONFIG_PATH = pkg_resources.resource_filename(__name__, "data/config.ini")
DEFAULT_CONFIG = ConfigParser(comment_prefixes=';', allow_no_value=True)
DEFAULT_CONFIG.read(DEFAULT_CONFIG_PATH)

class Config:

    def __init__(self):
        self.config_path = ONM_CONFIG_PATH
        self.config = ConfigParser(comment_prefixes=';', allow_no_value=True)
        self.config.read(self.config_path)
        print(self.config.sections())

    @property
    def transactions(self) -> str:
        path = self.config[ONM_SECTION].get(
            TRANSACTIONS, DEFAULT_CONFIG[ONM_SECTION][TRANSACTIONS])
        path = os.path.expanduser(path)
        return path

    def add_account(self, account_name: str, last_updated: str, source: str):
        self.config[account_name] = {}
        self.config[account_name]["source"] = source
        self.config[account_name]["last_updated"] = last_updated

    def update(self):
        with open(self.config_path, "w+") as f:
            self.config.write(f)

