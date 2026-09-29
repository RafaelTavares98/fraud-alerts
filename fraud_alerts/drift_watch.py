"""Watches the working point slip.

Fraud moves, because the other side adapts. A model with no watcher is a
model nobody is looking at. This compares each window against the first
one, and only shouts when the window is big enough for the fall to mean
something.
"""

SLIP = 0.30
ENOUGH_ALERTS = 20


def compare(windows, slip=SLIP, enough=ENOUGH_ALERTS):
    """Each window, with the ones that broke marked.

    Two ways to slip, and the second is the one that hides. Precision
    can fall, which is loud: the queue fills with rubbish. Or the model
    can simply stop firing, and the queue goes quiet while the fraud
    carries on. A watcher that only reads precision calls the second one
    healthy, because a queue of three alerts is easy to keep clean.
    """
    watched = []
    for window in windows:
        precision_fell = _fell(windows[0]["precision"], window["precision"], slip)
        recall_fell = _fell(windows[0]["recall"], window["recall"], slip)
        thin = window["alerts"] < enough
        judgeable = window.get("frauds", window["alerts"]) >= enough
        watched.append(
            {
                **window,
                "drifted": (precision_fell and not thin)
                or (recall_fell and judgeable),
                "too_small": thin and not judgeable,
            }
        )
    return watched


def _fell(first, now, slip):
    return first > 0 and (first - now) / first >= slip
