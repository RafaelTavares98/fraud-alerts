"""Picks the cut from the review capacity and the cost of being wrong.

Not the best F1. F1 does not know how many alerts a person can read in a
day, and it does not know that a missed fraud costs thirty times what a
wasted review costs.
"""

from fraud_alerts import queue_report


STEPS = 200


def choose(scores, target, capacity, days, fraud_cost, review_cost):
    """The threshold that pays most while the queue still fits."""
    _demand_a_capacity(capacity)
    affordable = [
        queue_report.at_threshold(
            scores, target, cut, days, fraud_cost, review_cost
        )
        for cut in _candidates(scores)
    ]
    fitting = [one for one in affordable if one["alerts_a_day"] <= capacity]
    if not fitting:
        return {"chosen": None, "reason": "no threshold keeps the queue inside capacity"}
    best = max(fitting, key=lambda one: one["net"])
    if best["net"] <= 0:
        return {"chosen": best, "reason": "no threshold pays for the reviews it costs"}
    return {"chosen": best, "reason": None}


def _candidates(scores):
    """Cuts taken from the scores themselves, not from an even grid.

    An even grid over 0 to 1 misses the answer whenever a model pushes
    almost every score to one end. On the real card data every useful
    cut sits above 0.99, and a grid of hundredths walked straight past
    all of them.
    """
    ordered = sorted(scores)
    step = max(len(ordered) // STEPS, 1)
    return sorted(set(ordered[::step]))


def _demand_a_capacity(capacity):
    if capacity < 1:
        raise ValueError(f"a capacity of {capacity} alerts a day is not a queue")
