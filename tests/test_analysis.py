from fraud_alerts import analysis


def test_it_finds_a_threshold_that_fits_the_queue(stream):
    result = analysis.pick_threshold(
        stream, "is_fraud", cutoff=80, capacity=200, fraud_cost=120, review_cost=4
    )
    best = result["chosen"]["chosen"]
    assert best["alerts_a_day"] <= 200
    assert best["recall"] > 0.5


def test_a_steady_stream_holds(stream):
    result = analysis.watch_drift(
        stream, "is_fraud", cutoff=60, threshold=0.5, delay_days=20
    )
    assert not any(one["drifted"] for one in result["watched"])


def test_the_planted_drift_is_caught(drifting):
    result = analysis.watch_drift(
        drifting, "is_fraud", cutoff=60, threshold=0.5, delay_days=20
    )
    assert any(one["drifted"] for one in result["watched"])
