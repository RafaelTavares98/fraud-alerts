"""Writes the two example streams the readme talks about.

Fixed seeds, so they come back identical. Not committed.
"""

import sys

from data import make_transactions


def main():
    steady = make_transactions.make_stream(
        transactions=40000, days=120, seed=3, fraud_rate=0.02
    )
    make_transactions.write_csv(steady, "data/transactions.csv")
    drifting = make_transactions.make_stream(
        transactions=40000, days=120, seed=3, fraud_rate=0.02, drift_day=80
    )
    make_transactions.write_csv(drifting, "data/transactions_drifting.csv")
    print("wrote data/transactions.csv and data/transactions_drifting.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
