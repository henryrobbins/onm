import os
import re
from typing import Optional
import click
import tempfile
import subprocess
import pandas as pd

from onm import main
from onm.common import Account, SourceType
from .config import Config


from onm.category import MINT_ONM_CATEGORY_MAPPING

# TODO: Check more than one place for config file
ONM_CONFIG_PATH = "~/.config/onm/config"
ONM_INI_PATH = "~/.config/onm/config.ini"
# DEFAULT_DIRECTORY = "~/onm"
APP_FILES = ["index.html", "oauth.html", "server.js", "package.json"]


@click.group()
def cli():
    """Main entry point."""
    pass


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
    df["category"] = df["Category"].apply(lambda x: MINT_ONM_CATEGORY_MAPPING[x])
    df["date"] = pd.to_datetime(df["Date"]).dt.date
    df["description"] = df["Description"]
    df["amount"] = df["Amount"]
    df["type"] = df["Transaction Type"]
    df = df[["date", "description", "category", "amount", "type", "account"]]

    last_updated = df.groupby("account").date.max().to_dict()

    config = Config()

    for account_name in last_updated:
        account = Account(account_name=account_name, balance=0)
        config.update_account(account)

    df.to_csv(config.transactions, index=False)

    config.update()


def _editor_account_selection(account_names):
    tmp = tempfile.NamedTemporaryFile()

    with open(tmp.name, "w") as f:
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
@click.option("-n", "--name", required=True, type=str, help="Name of source")
@click.option("-t", "--type", required=True, type=str, help="Type of source")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file")
def add_source(type: str, name: str, config: Optional[str] = None):
    main.add_source(SourceType(type), name, Config(config))


@cli.command()
@click.option("-n", "--name", required=True, type=str, help="Name of source")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file")
def update_source(name: str, config: Optional[str] = None):
    main.update_source(name, Config(config))


@cli.command()
@click.option("-n", "--name", required=True, type=str, help="Name of source")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file")
def sync_source(name: str, config: Optional[str] = None):
    main.sync_source(name, Config(config))


if __name__ == "__main__":
    cli()
