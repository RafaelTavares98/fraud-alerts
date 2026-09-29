import pytest

from fraud_alerts import queue_report


SCORES = [0.9, 0.8, 0.4, 0.1]
TARGET = [1, 0, 1, 0]


def test_a_high_cut_sends_few_alerts():
    measured = queue_report.at_threshold(SCORES, TARGET, threshold=0.85)
    assert measured["alerts"] == 1
    assert measured["precision"] == 1.0
    assert measured["recall"] == 0.5


def test_a_low_cut_catches_everything_and_wastes_reviews():
    measured = queue_report.at_threshold(SCORES, TARGET, threshold=0.05)
    assert measured["recall"] == 1.0
    assert measured["precision"] == 0.5


def test_a_cut_nobody_passes_reports_zero_rather_than_dividing_by_it():
    measured = queue_report.at_threshold(SCORES, TARGET, threshold=0.99)
    assert measured["alerts"] == 0
    assert measured["precision"] == 0.0


def test_the_money_line_counts_both_directions():
    measured = queue_report.at_threshold(
        SCORES, TARGET, threshold=0.05, fraud_cost=100, review_cost=10
    )
    assert measured["net"] == pytest.approx(2 * 100 - 4 * 10)
