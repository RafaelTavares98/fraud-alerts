"""Runs the steps in the order that keeps the answer honest.

Time order first, then the split, then the model. The labels that would
not have arrived yet never reach the measurement.
"""

from fraud_alerts import drift_watch
from fraud_alerts import features
from fraud_alerts import label_delay
from fraud_alerts import model
from fraud_alerts import queue_report
from fraud_alerts import threshold_choice
from fraud_alerts import time_order
from fraud_alerts import verdict


def pick_threshold(frame, target, cutoff, capacity, fraud_cost, review_cost):
    scored, scores = _score_the_future(frame, target, cutoff)
    days = max(scored["day"].max() - scored["day"].min(), 1)
    chosen = threshold_choice.choose(
        list(scores), list(scored[target]), capacity, days, fraud_cost, review_cost
    )
    return {"chosen": chosen, "verdict": verdict.on_threshold(chosen)}


def watch_drift(frame, target, cutoff, threshold, delay_days, windows=3):
    scored, scores = _score_the_future(frame, target, cutoff)
    today = frame["day"].max()
    settled = label_delay.usable(scored.assign(score=scores), today, delay_days)
    label_delay.demand_settled(settled, today, delay_days)
    measured = [
        _one_window(part, target, threshold, number)
        for number, part in enumerate(_cut_into(settled, windows), start=1)
    ]
    watched = drift_watch.compare(measured)
    return {"watched": watched, "verdict": verdict.on_drift(watched)}


def _score_the_future(frame, target, cutoff):
    time_order.demand_order(frame)
    past, future = time_order.split_at_day(frame, cutoff)
    fitted = model.fit(features.build(past), past[target])
    return future, model.score(fitted, features.build(future))


def _cut_into(frame, windows):
    size = len(frame) // windows
    return [frame.iloc[number * size:(number + 1) * size] for number in range(windows)]


def _one_window(part, target, threshold, number):
    measured = queue_report.at_threshold(
        list(part["score"]), list(part[target]), threshold
    )
    return {**measured, "window": number}
