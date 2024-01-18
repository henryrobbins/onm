from abc import ABC
from onm.connection.csv_reader import CsvReader, AmexCsvReader, AppleCsvReader
from onm.sync import CsvSyncCursor
from .connection import (
    Connection,
    AccountBalance,
    TransactionType,
    Transaction,
    SyncTransactionsResponse,
)
from typing import List, Optional


class CsvConnection(Connection, ABC):
    def __init__(self, csv_path: str, account_name: str, csv_reader: CsvReader):
        self._csv_path = csv_path
        self._account_name = account_name
        self._csv_reader = csv_reader

    def get_account_balances(self) -> List[AccountBalance]:
        return [
            AccountBalance(
                account_name=self._account_name,
                account_id=self._account_name,
                balance=0,
            )
        ]

    def sync_transactions(
        self, sync_cursor: Optional[CsvSyncCursor] = None
    ) -> SyncTransactionsResponse:
        df = self._csv_reader.read_csv(self._csv_path)

        if sync_cursor is not None:
            df = df[df["date"] > sync_cursor.latest_transaction_date]
        if len(df) == 0:
            return SyncTransactionsResponse(transactions=[], sync_cursor=sync_cursor)
        latest_transaction_date = max(df["date"])

        transactions = []
        for _, row in df.iterrows():
            transactions.append(
                Transaction(
                    date=row["date"],
                    description=row["description"],
                    amount=row["amount"],
                    primary_category=row["primary_category"],
                    detailed_category=row["detailed_category"],
                    account_id="apple",
                    type=TransactionType(row["type"]),
                )
            )

        return SyncTransactionsResponse(
            transactions=transactions,
            sync_cursor=CsvSyncCursor(
                latest_transaction_date=latest_transaction_date.isoformat()
            ),
        )


class AmexCsvConnection(CsvConnection):
    def __init__(self, csv_path: str):
        super().__init__(csv_path, "amex", AmexCsvReader)


class AppleCsvConnection(CsvConnection):
    def __init__(self, csv_path: str):
        super().__init__(csv_path, "apple", AppleCsvReader)
