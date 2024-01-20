from onm.config import Config
from onm.common import SourceType
from onm.source.source_factory import SourceFactory
from onm.connection.connection_factory import ConnectionFactory
from onm.database.database_factory import DatabaseFactory


def add_source(type: SourceType, name: str, config: Config) -> None:
    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    source = SourceFactory.create_source(type=type, name=name, config=config)
    database.add_source(source)


def update_source(name: str, config: Config) -> None:
    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    source = database.get_source(name)
    if source.type is not SourceType.PLAID:
        # TODO: Any warning? Perhaps in verbose mode?
        return
    source.update_link(config)


def sync_source(
    name: str,
    config: Config,
    csv_path: str = None,
) -> None:
    database_config = config.get_database_config()
    database = DatabaseFactory.create_database(database_config)
    source = database.get_source(name)
    connection = ConnectionFactory.create_connection(
        source.type, config, csv_path=csv_path
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
