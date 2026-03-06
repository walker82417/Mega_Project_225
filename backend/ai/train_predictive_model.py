"""Train a baseline anomaly model for predictive maintenance.

Usage:
    python backend/ai/train_predictive_model.py --data data/machine_data.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_CANDIDATES = [
    "temperature",
    "vibration",
    "current",
    "pressure",
    "humidity",
    "rpm",
]


def pick_features(df: pd.DataFrame) -> list[str]:
    cols = [c for c in FEATURE_CANDIDATES if c in df.columns]
    if len(cols) < 3:
        raise ValueError(
            "Dataset must contain at least 3 numeric features such as temperature, vibration, and current."
        )
    return cols


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to CSV dataset")
    parser.add_argument("--out", default="backend/ai/model.joblib", help="Output model file")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    features = pick_features(df)
    X = df[features].dropna()

    X_train, _ = train_test_split(X, test_size=0.2, random_state=42)

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("detector", IsolationForest(contamination=0.08, random_state=42)),
        ]
    )
    model.fit(X_train)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": features}, out)
    print(f"Saved model to {out} with features={features} and training rows={len(X_train)}")


if __name__ == "__main__":
    main()
