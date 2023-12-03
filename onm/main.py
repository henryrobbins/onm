import os
import yaml
import click
import shutil
import subprocess
import webbrowser
import pandas as pd
from tabulate import tabulate
from tinydb import TinyDB

import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = "~/.config/onm/config"
# DEFAULT_DIRECTORY = "~/onm"
APP_FILES = ['index.html', 'server.js', 'package.json']


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


def plaid_client(config):
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
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
def link_account():
    """Link an account via Plaid."""
    config = read_config()
    directory = os.path.expanduser(config['directory'])
    app_dir = os.path.join(directory, '.onm', 'app')

    # Get Access Token from Link
    app = subprocess.Popen("npm start", shell=True, cwd=app_dir,
                           stdout=subprocess.PIPE)
    webbrowser.open("http://localhost:8080")
    access_token = input("Access token: ")
    app.terminate()

    # Save Access Token
    directory = os.path.expanduser(config['directory'])
    table_path = os.path.join(directory, "access.json")
    db = TinyDB(table_path)
    db.insert({"access_token": access_token})


@cli.command()
def sync_accounts():
    """Sync accounts."""
    # Get all Access Tokens
    config = read_config()
    directory = os.path.expanduser(config['directory'])
    db = TinyDB(os.path.join(directory, "access.json"))
    access_tokens = [x["access_token"] for x in db.all()]

    # Pull all account data
    client = plaid_client(config)
    accounts = []
    for access_token in access_tokens:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        accounts += response['accounts']

    # Write account data to database
    db = TinyDB(os.path.join(directory, "accounts.json"))
    for account in accounts:
        db.insert({
            "account_id": account["account_id"],
            "balance": account["balances"]["available"],
            "official_name": account["official_name"]
        })


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
