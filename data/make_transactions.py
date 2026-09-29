"""Invents a stream of card transactions with a known fraud rule.

Half way through, the rule changes. That is deliberate: the drift watch
has to notice, and a watcher that has never seen real drift has never
been tested.

Before the change, fraud is a big payment at night. After it, fraud is a
small payment from a country the customer has never used.
"""

import csv
import random


COLUMNS = [
    "transaction_id",
    "customer_id",
    "day",
    "hour",
    "amount",
    "country",
    "is_fraud",
]
HOME = "BR"
ELSEWHERE = ["PA", "NG", "RO", "VN"]


def make_stream(transactions, days, seed, fraud_rate=0.01, drift_day=None):
    """Rows in time order, one per transaction."""
    source = random.Random(seed)
    habits = _habits(source, customers=200)
    rows = []
    for number in range(transactions):
        day = number * days // transactions
        rows.append(_one(source, number, day, habits, fraud_rate, drift_day))
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _habits(source, customers):
    return {
        f"k{number}": source.uniform(20, 300) for number in range(customers)
    }


def _one(source, number, day, habits, fraud_rate, drift_day):
    customer = source.choice(list(habits))
    usual = habits[customer]
    fraudulent = source.random() < fraud_rate
    after_drift = drift_day is not None and day >= drift_day
    amount, hour, country = _shape(source, usual, fraudulent, after_drift)
    return {
        "transaction_id": f"t{number}",
        "customer_id": customer,
        "day": day,
        "hour": hour,
        "amount": round(amount, 2),
        "country": country,
        "is_fraud": int(fraudulent),
    }


def _shape(source, usual, fraudulent, after_drift):
    """Fraud and ordinary life overlap, because they do.

    A rule with no overlap produces a model that scores 100% and teaches
    nobody anything. Some honest people buy a fridge at two in the
    morning, and plenty of fraud looks like a normal Tuesday.
    """
    if not fraudulent:
        return _ordinary(source, usual)
    if after_drift:
        return (
            max(source.gauss(usual * 0.15, usual * 0.1), 1),
            source.randint(0, 23),
            source.choice(ELSEWHERE) if source.random() < 0.6 else HOME,
        )
    return (
        usual * source.uniform(1.2, 4.0),
        source.randint(0, 5) if source.random() < 0.6 else source.randint(6, 23),
        HOME,
    )


def _ordinary(source, usual):
    """Most payments are dull. A few are large, a few are late at night."""
    amount = max(source.gauss(usual, usual * 0.45), 1)
    if source.random() < 0.05:
        amount *= source.uniform(2.0, 5.0)
    hour = source.randint(0, 5) if source.random() < 0.08 else source.randint(6, 23)
    return amount, hour, HOME
