from .database import DatabaseType, Database
from .csv_database import CsvDatabase


class DatabaseFactory():

    @staticmethod
    def create_database(type: DatabaseType, *args, **kwargs) -> Database:
        if type == DatabaseType.CSV:
            return CsvDatabase(*args, **kwargs)
        else:
            raise ValueError("Unknown database type")
