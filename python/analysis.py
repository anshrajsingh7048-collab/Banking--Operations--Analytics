"""
Basic exploratory analysis for the synthetic transaction dataset.
Run after cleaning: python python/analysis.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "transactions_cleaned.csv"
OUT = ROOT / "data" / "analysis_outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(INPUT, parse_dates=["transaction_date"])
df["month"] = df["transaction_date"].dt.to_period("M").astype(str)

channel_summary = df.groupby("channel").agg(
    total_transactions=("transaction_id", "count"),
    successful_transactions=("status", lambda s: (s == "Success").sum()),
    failed_transactions=("status", lambda s: (s == "Failed").sum()),
    pending_transactions=("status", lambda s: (s == "Pending").sum()),
    avg_processing_time_sec=("processing_time_sec", "mean"),
    total_amount_inr=("amount_inr", "sum"),
).reset_index()
channel_summary["failure_rate_pct"] = (
    100 * channel_summary["failed_transactions"] / channel_summary["total_transactions"]
).round(2)
channel_summary["success_rate_pct"] = (
    100 * channel_summary["successful_transactions"] / channel_summary["total_transactions"]
).round(2)
channel_summary.to_csv(OUT / "channel_summary.csv", index=False)

daily_summary = df.groupby("transaction_date").agg(
    total_transactions=("transaction_id", "count"),
    failed_transactions=("status", lambda s: (s == "Failed").sum()),
    successful_transactions=("status", lambda s: (s == "Success").sum()),
).reset_index()
daily_summary["failure_rate_pct"] = (
    100 * daily_summary["failed_transactions"] / daily_summary["total_transactions"]
).round(2)
daily_summary.to_csv(OUT / "daily_summary.csv", index=False)

failure_summary = (
    df[df["status"] == "Failed"]
    .groupby(["failure_reason", "channel"])
    .size().reset_index(name="failed_transactions")
    .sort_values("failed_transactions", ascending=False)
)
failure_summary.to_csv(OUT / "failure_reason_summary.csv", index=False)

region_summary = df.groupby("region").agg(
    total_transactions=("transaction_id", "count"),
    failed_transactions=("status", lambda s: (s == "Failed").sum()),
    complaints=("complaint_flag", "sum"),
    avg_processing_time_sec=("processing_time_sec", "mean"),
).reset_index()
region_summary["failure_rate_pct"] = (
    100 * region_summary["failed_transactions"] / region_summary["total_transactions"]
).round(2)
region_summary.to_csv(OUT / "region_summary.csv", index=False)

print("Analysis outputs written to data/analysis_outputs/")
print("\\nChannel summary:")
print(channel_summary.round(2).to_string(index=False))
