from fraud_alerts import drift_watch


def window(number, precision, alerts=200, recall=0.5, frauds=100):
    return {
        "window": number,
        "precision": precision,
        "recall": recall,
        "alerts": alerts,
        "frauds": frauds,
    }


def test_steady_windows_are_left_alone():
    watched = drift_watch.compare([window(1, 0.30), window(2, 0.28)])
    assert not any(one["drifted"] for one in watched)


def test_a_third_lost_is_called_drift():
    watched = drift_watch.compare([window(1, 0.30), window(2, 0.18)])
    assert watched[1]["drifted"]


def test_a_small_window_is_not_accused():
    watched = drift_watch.compare(
        [window(1, 0.30), window(2, 0.05, alerts=4, frauds=2)]
    )
    assert not watched[1]["drifted"]
    assert watched[1]["too_small"]


def test_a_queue_that_goes_quiet_is_drift_too():
    """Precision looks perfect on three alerts, and the fraud carries on."""
    watched = drift_watch.compare(
        [window(1, 0.30, recall=0.60), window(2, 1.00, alerts=3, recall=0.02)]
    )
    assert watched[1]["drifted"]


def test_a_rising_window_is_not_drift():
    watched = drift_watch.compare([window(1, 0.30), window(2, 0.60)])
    assert not watched[1]["drifted"]
