import hashlib
from pathlib import Path

import pandas as pd

SOURCE = Path("data/raw/paysim.csv")
OUTPUT = Path("data/processed/transactions.parquet")


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Dataset not found: {SOURCE}")

    df = pd.read_csv(SOURCE)

    required = {
        "step",
        "type",
        "amount",
        "nameOrig",
        "nameDest",
        "isFraud",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.loc[df["amount"] > 0].copy()

    result = pd.DataFrame(
        {
            "transaction_id": [f"paysim_{i}" for i in range(len(df))],
            "event_time": pd.to_datetime(df["step"], unit="h", utc=True),
            "sender_id": df["nameOrig"].astype(str),
            "receiver_id": df["nameDest"].astype(str),
            "amount": pd.to_numeric(df["amount"], errors="raise"),
            "transaction_type": df["type"].astype(str),
            "is_fraud": df["isFraud"].astype(int),
        }
    )

    # These are simulated fields because PaySim does not provide real
    # device, IP, or location identifiers.
    result["device_id"] = result["sender_id"].map(
        lambda value: stable_id("device", value)
    )
    result["ip_id"] = result["sender_id"].map(
        lambda value: stable_id("ip", value)
    )
    result["location_id"] = result["sender_id"].map(
        lambda value: stable_id("location", value)
    )

    if result["transaction_id"].duplicated().any():
        raise ValueError("Duplicate transaction IDs found")

    if (result["amount"] <= 0).any():
        raise ValueError("Non-positive transaction amounts found")

    if result["is_fraud"].isin([0, 1]).all() is False:
        raise ValueError("is_fraud must contain only 0 or 1")

    result = result.sort_values(
        ["event_time", "transaction_id"],
        kind="mergesort",
    ).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUTPUT, index=False)

    print(f"Saved {len(result):,} rows to {OUTPUT}")


if __name__ == "__main__":
    main()