"""Reads the transactions and complains about what is missing."""

import pandas


REQUIRED = ["transaction_id", "customer_id", "day", "amount"]


def read_stream(path, target):
    frame = pandas.read_csv(path)
    _demand_columns(frame, target)
    return frame


def _demand_columns(frame, target):
    missing = [name for name in REQUIRED + [target] if name not in frame]
    if missing:
        raise ValueError(f"the file has no column called {', '.join(missing)}")
