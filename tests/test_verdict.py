from fraud_alerts import verdict


GOOD = {
    "chosen": {
        "threshold": 0.83,
        "alerts_a_day": 196,
        "precision": 0.31,
        "recall": 0.62,
        "caught": 61,
        "frauds": 98,
        "net": 6536,
    },
    "reason": None,
}


def test_a_workable_queue_says_ship_it():
    decided = verdict.on_threshold(GOOD)
    assert decided["verdict"] == verdict.SHIP
    assert "61 of 98" in decided["reason"]


def test_a_queue_that_never_fits_says_do_not_ship():
    decided = verdict.on_threshold({"chosen": None, "reason": "no room"})
    assert decided["verdict"] == verdict.NO_ROOM
    assert "too small" in decided["reason"]


def test_a_queue_that_loses_money_says_do_not_ship():
    decided = verdict.on_threshold({**GOOD, "reason": "does not pay"})
    assert decided["verdict"] == verdict.NO_ROOM
    assert "loses money" in decided["reason"]


def test_a_slipped_window_says_retrain():
    watched = [
        {"window": 1, "precision": 0.30, "drifted": False},
        {"window": 2, "precision": 0.15, "drifted": True},
    ]
    assert verdict.on_drift(watched)["verdict"] == verdict.RETRAIN


def test_steady_windows_say_holding():
    watched = [
        {"window": 1, "precision": 0.30, "drifted": False},
        {"window": 2, "precision": 0.29, "drifted": False},
    ]
    assert verdict.on_drift(watched)["verdict"] == verdict.HOLDING
