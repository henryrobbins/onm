import pandas as pd
from onm.sync import CsvSyncCursor
from .connection import (
    Connection,
    AccountBalance,
    TransactionType,
    Transaction,
    SyncTransactionsResponse,
)
from typing import List, Optional


class AmexCsvConnection(Connection):
    def __init__(self, csv_path: str):
        self._csv_path = csv_path

    def get_account_balances(self) -> List[AccountBalance]:
        return [AccountBalance(account_name="amex", account_id="amex", balance=0)]

    def sync_transactions(
        self, sync_cursor: Optional[CsvSyncCursor] = None
    ) -> SyncTransactionsResponse:
        # f"https://global.americanexpress.com/spending-report/custom?from={start_date}&to={end_date}"
        df = pd.read_csv(self._csv_path)
        df["category"] = df["Category"]
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df["type"] = df["Amount"].apply(lambda x: "debit" if x < 0 else "credit")
        df["amount"] = df["Amount"].abs()
        df["description"] = df["Description"]
        df = df[["date", "description", "category", "amount", "type"]]

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
                    category=row["category"],
                    account_id="amex",
                    type=TransactionType(row["type"]),
                )
            )

        return SyncTransactionsResponse(
            transactions=transactions,
            sync_cursor=CsvSyncCursor(
                latest_transaction_date=latest_transaction_date.isoformat()
            ),
        )
