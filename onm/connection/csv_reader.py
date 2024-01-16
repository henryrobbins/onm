from abc import ABC, abstractmethod

import pandas as pd


class CsvReader(ABC):
    @abstractmethod
    def read_csv(path: str) -> pd.DataFrame:
        pass


class AmexCsvReader(CsvReader):
    @staticmethod
    def read_csv(path: str) -> pd.DataFrame:
        # f"https://global.americanexpress.com/spending-report/custom?from={start_date}&to={end_date}"
        df = pd.read_csv(path)
        df["category"] = df["Category"]
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df["type"] = df["Amount"].apply(lambda x: "debit" if x < 0 else "credit")
        df["amount"] = df["Amount"].abs()
        df["description"] = df["Description"]
        df = df[["date", "description", "category", "amount", "type"]]
        return df


class AppleCsvReader(CsvReader):
    @staticmethod
    def read_csv(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        df["category"] = df["Category"]
        df["date"] = pd.to_datetime(df["Transaction Date"]).dt.date
        df["description"] = df["Description"]
        df["amount"] = df["Amount (USD)"].abs()
        df["type"] = (
            df["Type"].replace("Purchase", "debit").replace("Payment", "credit")
        )
        df = df[["date", "description", "category", "amount", "type"]]
        return df
