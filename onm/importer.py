import pandas as pd
from enum import Enum

COLUMNS = ["date", "description", "category", "amount", "type", "account"]


class Source(Enum):
    CSV = "csv"


class CSV(Enum):
    APPLE = "apple"
    AMEX = "amex"


def import_transactions_csv(file_path, csv_type: CSV, account_name = None):
    if csv_type == CSV.APPLE:
        return _import_apple_card_transactions_csv(file_path, account_name)
    elif csv_type == CSV.AMEX:
        return _import_amex_transactions_csv(file_path, account_name)
    else:
        raise ValueError(f"unknown error")


def _import_apple_card_transactions_csv(file_path, account_name = None):
    df = pd.read_csv(file_path)
    df["account"] = account_name or "Apple Card"
    df["category"] = df["Category"]
    df["date"] = pd.to_datetime(df["Transaction Date"]).dt.date
    df["description"] = df["Description"]
    df["amount"] = df["Amount (USD)"].abs()
    df["type"] = df["Type"] \
        .replace("Purchase", "debit") \
        .replace("Payment", "credit")
    df = df[COLUMNS]
    return df


# f"https://global.americanexpress.com/spending-report/custom?from={start_date}&to={end_date}"
def _import_amex_transactions_csv(file_path, account_name = None):
    df = pd.read_csv(file_path)
    df["account"] = account_name or "American Express Card"
    df["category"] = df["Category"]
    df["date"] = pd.to_datetime(df["Date"]).dt.date
    df["type"] = df["Amount"].apply(lambda x: "debit" if x < 0 else "credit")
    df["amount"] = df["Amount"].abs()
    df["description"] = df["Description"]
    df = df[COLUMNS]
    return df
