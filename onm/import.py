import pandas as pd

COLUMNS = ["date", "description", "category", "amount", "type", "account"]


def import_apple_card_transactions(file_path, account_name = "Apple Card"):
    df = pd.read_csv(file_path)
    df["account"] = account_name
    df["category"] = df["Category"]
    df["date"] = pd.to_datetime(df["Transaction Date"])
    df["description"] = df["Description"]
    df["amount"] = df["Amount (USD)"].abs()
    df["type"] = df["Type"] \
        .replace("Purchase", "debit") \
        .replace("Payment", "credit")
    df = df[COLUMNS]
    return df


# f"https://global.americanexpress.com/spending-report/custom?from={start_date}&to={end_date}"
def import_amex_transactions(file_path, account_name = "American Express Card"):
    df = pd.read_csv(file_path)
    df["account"] = account_name
    df["category"] = df["Category"]
    df["date"] = pd.to_datetime(df["Date"])
    df["type"] = df["Amount"].apply(lambda x: "debit" if x < 0 else "credit")
    df["amount"] = df["Amount"].abs()
    df["description"] = df["Description"]
    df = df[COLUMNS]
    return df
