from .database import DatabaseType, Database, DatabaseConfiguration
from .plain_text_database import PlainTextDatabase


class DatabaseFactory:
    @staticmethod
    def create_database(database_config: DatabaseConfiguration) -> Database:
        type = database_config.type
        if type == DatabaseType.PLAIN_TEXT:
            return PlainTextDatabase(**database_config.parameters)
        else:
            raise ValueError("Unknown database type")
