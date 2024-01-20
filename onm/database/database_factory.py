from .database import DatabaseType, Database
from .plain_text_database import PlainTextDatabase


class DatabaseFactory:
    @staticmethod
    def create_database(type: DatabaseType, *args, **kwargs) -> Database:
        if type == DatabaseType.PLAIN_TEXT:
            return PlainTextDatabase(*args, **kwargs)
        else:
            raise ValueError("Unknown database type")
