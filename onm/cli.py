import os
import re
import yaml
import click
import shutil
import tempfile
import subprocess
import pandas as pd
from .config import Config
from .account import Account
from .importer import import_transactions_csv
from .transaction import transaction_table
from .source import PlaidLink, PlaidSource, get_plaid_api
from tabulate import tabulate
from tinydb import TinyDB

import plaid
from plaid.api import plaid_api

from .constants import MINT_CATEGORY_MAP

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = "~/.config/onm/config"
ONM_INI_PATH = "~/.config/onm/config.ini"
# DEFAULT_DIRECTORY = "~/onm"
APP_FILES = ['index.html', 'oauth.html', 'server.js', 'package.json']


def read_config():
    config_path = os.path.expanduser(ONM_CONFIG_PATH)
    with open(config_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError:
            ValueError("Error reading config file.")
    update_app_env(config)
    return config


def get_app_dir(config):
    directory = os.path.expanduser(config['directory'])
    return os.path.join(directory, '.onm', 'app')


def update_app_env(config):
    app_dir = get_app_dir(config)
    app_env_file_path = os.path.join(app_dir, '.env')
    with open(app_env_file_path, 'w') as f:
        f.write(f"PLAID_CLIENT_ID={config['plaid_client_id']}\n")
        f.write(f"PLAID_SECRET={config['plaid_secret']}\n")
        f.write(f"PLAID_ENV={config['plaid_env']}")


def print_table(df, cols=None):
    if cols is None:
        cols = df.columns
    rows = []
    for index, row in df.iterrows():
        rows.append(list(row[cols]))
    print(tabulate(rows, headers=cols, tablefmt='orgtbl'))


def get_host(config):
    env = config["plaid_env"]
    if env == "sandbox":
        return plaid.Environment.Sandbox
    elif env == "development":
        return plaid.Environment.Development
    elif env == "production":
        return plaid.Environment.Production


def plaid_client(config):
    configuration = plaid.Configuration(
        host=get_host(config),
        api_key={
            'clientId': config['plaid_client_id'],
            'secret': config['plaid_secret'],
        }
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


@click.group()
def cli():
    """Main entry point."""
    pass


@cli.command()
def setup():
    """Runs setup required to connect bank accounts via Plaid."""
    # Copy app-related files to onm directory
    config = read_config()
    module_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(module_dir, 'app')
    directory = os.path.expanduser(config['directory'])
    app_dir = os.path.join(directory, '.onm', 'app')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    for data_file in APP_FILES:
        src_file = os.path.join(src_dir, data_file)
        dest_file = os.path.join(app_dir, data_file)
        shutil.copy(src_file, dest_file)
    # Install dependencies
    subprocess.Popen("npm install", shell=True, cwd=app_dir)


@cli.command()
@click.argument("mint_export_path", type=click.Path(exists=True))
def import_mint_data(mint_export_path):
    """TODO"""
    df = pd.read_csv(mint_export_path)
    account_names = df["Account Name"].unique().tolist()
    # TODO: Add option to select accounts one at a time within terminal
    selected_accounts = _editor_account_selection(account_names)

    df = df[df["Account Name"].isin(selected_accounts)]
    df["account"] = df["Account Name"].apply(lambda x: selected_accounts[x])
    df["category"] = df["Category"].apply(lambda x: MINT_CATEGORY_MAP[x])
    df["date"] = pd.to_datetime(df["Date"]).dt.date
    df["description"] = df["Description"]
    df["amount"] = df["Amount"]
    df["type"] = df["Transaction Type"]
    df = df[["date", "description", "category", "amount", "type", "account"]]

    last_updated = df.groupby("account").date.max().to_dict()

    config = Config()

    for account_name in last_updated:
        account = Account(
            account_name=account_name,
            last_updated=last_updated[account_name]
        )
        config.update_account(account)

    df.to_csv(config.transactions, index=False)

    config.update()


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("account_name", type=str)
def import_transactions(file_path, account_name):
    config = Config()
    account = config.get_account(account_name)

    df = pd.read_csv(config.transactions)
    new_df = import_transactions_csv(
        file_path=file_path,
        csv_type=account.csv_type,
        account_name=account_name
    )

    # update transactions
    # TODO: only add transactions occurring after last_updated
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(config.transactions, index=False)

    # update account
    account.last_updated = new_df["date"].max()
    config.update_account(account)


def _editor_account_selection(account_names):
    tmp = tempfile.NamedTemporaryFile()

    with open(tmp.name, 'w') as f:
        lines = [f"{i+1}. {name}" for i, name in enumerate(account_names)]
        f.write("\n".join(lines))

    editor = os.environ.get("EDITOR", "vim")
    subprocess.call([editor, tmp.name])

    with open(tmp.name) as f:
        selection = f.read()
        pattern = re.compile(r"^(\d+)\. (.+)$", re.MULTILINE)
        matched = re.findall(pattern, selection)

    print(matched)
    print(account_names)

    return {account_names[int(i) - 1]: rename for i, rename in matched}


@cli.command()
@click.option('-c', '--config', help='Configuration file')
def link_item(config):
    """Link an item via Plaid."""
    config = Config(config)
    plaid_configuration = config.get_plaid_config()
    plaid_api = get_plaid_api(plaid_configuration)
    plaid_link = PlaidLink(plaid_api)
    access_token = plaid_link.get_access_token()
    plaid_source = PlaidSource(plaid_api)
    account_balances = plaid_source.get_account_balances(access_token)

    account_names = {a.account_name: a for a in account_balances.keys()}
    selected_accounts = _editor_account_selection(list(account_names.keys()))

    selected_account_balances = {}
    for current_name, rename in selected_accounts.items():
        account = account_names[current_name]
        balance = account_balances[account]
        account.account_name = rename
        selected_account_balances[account] = balance

    # TODO: Currently doing nothing with account balances
    for account in selected_account_balances.keys():
        config.update_account(account)


@cli.command()
@click.argument("account_name", type=str)
def sync_account(account_name: str):
    """Sync account"""
    config = Config()
    plaid_config = config.get_plaid_config()
    client = PlaidAPI(plaid_config)
    account = config.get_account(account_name)
    transactions = client.get_transactions(account)
    print(transaction_table(transactions))
    # TODO Update transactions table appropriately


@cli.command()
def accounts():
    """Show accounts."""
    config = read_config()
    directory = os.path.expanduser(config['directory'])
    db = TinyDB(os.path.join(directory, "accounts.json"))
    df = pd.DataFrame(db.all())
    print_table(df)


if __name__ == '__main__':
    cli()
