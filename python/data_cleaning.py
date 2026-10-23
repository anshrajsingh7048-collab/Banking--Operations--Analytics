"""
Clean and validate the synthetic banking operations dataset.
Run: python python/data_cleaning.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "transactions_synthetic.csv"
OUTPUT = ROOT / "data" / "transactions_cleaned.csv"
REPORT = ROOT / "data" / "data_quality_report.txt"

df = pd.read_csv(INPUT, parse_dates=["transaction_date"])
starting_rows = len(df)

# Standardise text fields
for col in ["channel", "transaction_type", "status", "failure_reason", "region"]:
    df[col] = df[col].astype("string").str.strip()

df["channel"] = df["channel"].str.title().replace({
    "Upi": "UPI",
    "Internet Banking": "Internet Banking",
    "Mobile Banking": "Mobile Banking",
    "Cards": "Cards",
})
df["status"] = df["status"].str.title()
df["transaction_id"] = df["transaction_id"].astype("string").str.strip()

# Remove duplicate transaction IDs, retaining the first occurrence
df = df.drop_duplicates(subset=["transaction_id"], keep="first")

# Numeric validation
df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
df["processing_time_sec"] = pd.to_numeric(df["processing_time_sec"], errors="coerce")
df["complaint_flag"] = pd.to_numeric(df["complaint_flag"], errors="coerce").fillna(0).astype(int)

invalid_amount = (df["amount_inr"] < 0).sum()
invalid_processing = (df["processing_time_sec"] < 0).sum()

# Mark invalid numeric values as missing, rather than silently changing them
df.loc[df["amount_inr"] < 0, "amount_inr"] = pd.NA
df.loc[df["processing_time_sec"] < 0, "processing_time_sec"] = pd.NA

# Ensure failed transactions have a usable reason
df.loc[(df["status"] == "Failed") & (df["failure_reason"].isna() | (df["failure_reason"] == "")),
       "failure_reason"] = "Unknown"

df.to_csv(OUTPUT, index=False, date_format="%Y-%m-%d")

report = [
    "SYNTHETIC BANKING TRANSACTION DATA QUALITY REPORT",
    f"Rows before deduplication: {starting_rows}",
    f"Rows after deduplication: {len(df)}",
    f"Duplicate transaction IDs removed: {starting_rows - len(df)}",
    f"Invalid negative amounts found: {invalid_amount}",
    f"Invalid negative processing times found: {invalid_processing}",
    "",
    "Missing values by column:",
    df.isna().sum().to_string(),
    "",
    "Status distribution:",
    df["status"].value_counts(dropna=False).to_string(),
]
REPORT.write_text("\n".join(report), encoding="utf-8")
print(f"Cleaned dataset saved to: {OUTPUT}")
print(f"Quality report saved to: {REPORT}")
