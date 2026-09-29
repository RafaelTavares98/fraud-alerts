import pandas
import pytest

from fraud_alerts import label_delay


FRAME = pandas.DataFrame({"day": [10, 80, 119, 120], "is_fraud": [1, 0, 1, 0]})


def test_a_transaction_from_yesterday_has_no_usable_label():
    usable = label_delay.usable(FRAME, today=120, delay_days=30)
    assert 119 not in list(usable["day"])


def test_a_transaction_from_months_ago_does():
    usable = label_delay.usable(FRAME, today=120, delay_days=30)
    assert 10 in list(usable["day"])


def test_measuring_unsettled_rows_is_refused():
    with pytest.raises(ValueError, match="not known yet"):
        label_delay.demand_settled(FRAME, today=120, delay_days=30)


def test_settled_rows_pass_the_same_check():
    settled = label_delay.usable(FRAME, today=120, delay_days=30)
    assert len(label_delay.demand_settled(settled, 120, 30)) == 2


def test_a_negative_delay_is_refused():
    with pytest.raises(ValueError, match="runs backwards"):
        label_delay.usable(FRAME, today=120, delay_days=-5)
