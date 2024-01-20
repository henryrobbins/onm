from onm.config import Config
from onm.common import SourceType
from onm.link.link_factory import LinkFactory
from onm.source.source_factory import SourceFactory
from onm.connection.connection_factory import ConnectionFactory
from onm.connection.plaid_connection import get_plaid_api
from onm.database.database_factory import DatabaseFactory
from typing import Type


def add_source(
    type: SourceType,
    name: str,
    config: Config,
    link_factory: Type[LinkFactory] = LinkFactory,
    connection_factory: Type[ConnectionFactory] = ConnectionFactory,
    source_factory: Type[SourceFactory] = SourceFactory,
) -> None:
    # TODO: Is this the right place for this? global config?
    if type == SourceType.PLAID:
        plaid_config = config.get_plaid_config()
        plaid_api = get_plaid_api(plaid_config)
    else:
        plaid_api = None
    source = source_factory.create_source(
        type=type,
        name=name,
        link_factory=link_factory,
        connection_factory=connection_factory,
        plaid_api=plaid_api,
    )
    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    database.add_source(source)


def update_source(
    name: str, config: Config, link_factory: Type[LinkFactory] = LinkFactory
) -> None:
    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    source = database.get_source(name)
    if source.type is not SourceType.PLAID:
        # TODO: Any warning? Perhaps in verbose mode?
        return
    plaid_config = config.get_plaid_config()
    plaid_api = get_plaid_api(plaid_config)
    source.update_link(link_factory=link_factory, plaid_api=plaid_api)


def sync_source(
    name: str,
    config: Config,
    connection_factory: Type[ConnectionFactory] = ConnectionFactory,
    csv_path: str = None,
) -> None:
    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    source = database.get_source(name)
    # TODO: Is this the right place for this? global config?
    if source.type is SourceType.PLAID:
        plaid_config = config.get_plaid_config()
        plaid_api = get_plaid_api(plaid_config)
    else:
        plaid_api = None
    connection = connection_factory.create_connection(
        source.type, plaid_api=plaid_api, csv_path=csv_path
    )
    account_balances = source.get_account_balances(connection)
    sync_cursor = database.get_sync_cursor(source)
    sync_transactions_res = source.sync_transactions(connection, sync_cursor)

    for account in account_balances:
        database.add_account(account)
    transactions = sync_transactions_res.transactions
    sync_cursor = sync_transactions_res.sync_cursor
    database.add_transactions(transactions)
    database.set_sync_cursor(source, sync_cursor)
