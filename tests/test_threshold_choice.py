import random

import pytest

from fraud_alerts import threshold_choice


def a_stream(frauds=100, honest=9900, seed=1):
    source = random.Random(seed)
    scores = [source.uniform(0.5, 1.0) for _ in range(frauds)]
    target = [1] * frauds
    scores += [source.uniform(0.0, 0.6) for _ in range(honest)]
    target += [0] * honest
    return scores, target


def test_a_smaller_queue_raises_the_cut():
    scores, target = a_stream()
    roomy = threshold_choice.choose(scores, target, 500, 10, 120, 4)["chosen"]
    tight = threshold_choice.choose(scores, target, 5, 10, 120, 4)["chosen"]
    assert tight["threshold"] > roomy["threshold"]
    assert tight["alerts_a_day"] <= 5


def test_a_costlier_fraud_lowers_the_cut():
    scores, target = a_stream()
    cheap = threshold_choice.choose(scores, target, 500, 10, 20, 4)["chosen"]
    dear = threshold_choice.choose(scores, target, 500, 10, 2000, 4)["chosen"]
    assert dear["threshold"] <= cheap["threshold"]


def test_a_queue_that_cannot_pay_is_said_out_loud():
    scores, target = a_stream(frauds=5, honest=9995)
    answer = threshold_choice.choose(scores, target, 500, 10, 1, 100)
    assert answer["reason"] == "no threshold pays for the reviews it costs"


def test_a_capacity_of_zero_is_refused():
    scores, target = a_stream()
    with pytest.raises(ValueError, match="not a queue"):
        threshold_choice.choose(scores, target, 0, 10, 120, 4)
