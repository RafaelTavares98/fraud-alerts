from data import make_transactions


def test_the_same_seed_makes_the_same_stream():
    first = make_transactions.make_stream(500, 30, seed=1)
    second = make_transactions.make_stream(500, 30, seed=1)
    assert first == second


def test_the_fraud_rate_lands_near_the_number_asked_for(rows):
    rate = sum(row["is_fraud"] for row in rows) / len(rows)
    assert 0.015 < rate < 0.025


def test_the_rows_come_out_in_time_order(rows):
    days = [row["day"] for row in rows]
    assert days == sorted(days)


def test_the_rule_changes_after_the_drift_day():
    rows = make_transactions.make_stream(6000, 100, seed=2, fraud_rate=0.05, drift_day=50)
    before = [r for r in rows if r["is_fraud"] and r["day"] < 50]
    after = [r for r in rows if r["is_fraud"] and r["day"] >= 50]
    assert all(row["country"] == "BR" for row in before)
    away = sum(row["country"] != "BR" for row in after) / len(after)
    assert away > 0.4, "after the drift most fraud comes from somewhere else"
    assert _average(before, "amount") > _average(after, "amount") * 3


def _average(rows, column):
    return sum(row[column] for row in rows) / len(rows)
