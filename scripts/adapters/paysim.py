import hashlib
from pathlib import Path

import pandas as pd

SOURCE = Path("data/raw/paysim.csv")
OUTPUT = Path("data/processed/transactions.parquet")


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Dataset not found: {SOURCE}")

    raw = pd.read_csv(SOURCE)

    required = {
        "step",
        "type",
        "amount",
        "nameOrig",
        "nameDest",
        "isFraud",
    }

    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    result = pd.DataFrame(
        {
            "transaction_id": [
                f"paysim_{index}" for index in raw.index
            ],
            "event_time": pd.to_datetime(
                raw["step"],
                unit="h",
                origin="1970-01-01",
                utc=True,
            ),
            "sender_id": raw["nameOrig"].astype(str),
            "receiver_id": raw["nameDest"].astype(str),
            "amount": pd.to_numeric(raw["amount"], errors="raise"),
            "transaction_type": raw["type"].astype(str),
            "is_fraud": raw["isFraud"].astype("int8"),
        },
        index=raw.index,
    )

    result["device_id"] = result["sender_id"].map(
        lambda value: stable_id("device", value)
    )
    result["ip_id"] = result["sender_id"].map(
        lambda value: stable_id("ip", value)
    )
    result["location_id"] = result["sender_id"].map(
        lambda value: stable_id("location", value)
    )

    if len(result) != len(raw):
        raise RuntimeError(
            f"Row count changed: raw={len(raw)}, processed={len(result)}"
        )

    if result["transaction_id"].nunique() != len(result):
        raise RuntimeError("Generated transaction IDs are not unique")

    if result["is_fraud"].sum() != raw["isFraud"].sum():
        raise RuntimeError("Fraud count changed during preprocessing")

    if result["amount"].lt(0).any():
        raise ValueError("Negative transaction amount found")

    result = result.sort_values(
        ["event_time", "transaction_id"],
        kind="mergesort",
    ).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUTPUT, index=False)

    print(f"Raw rows: {len(raw):,}")
    print(f"Processed rows: {len(result):,}")
    print(f"Raw fraud rows: {raw['isFraud'].sum():,}")
    print(f"Processed fraud rows: {result['is_fraud'].sum():,}")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()