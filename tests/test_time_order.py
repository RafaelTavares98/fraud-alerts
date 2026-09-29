import pytest

from fraud_alerts import time_order


def test_an_ordered_stream_passes(stream):
    assert len(time_order.demand_order(stream)) == len(stream)


def test_a_shuffled_stream_names_the_first_bad_row(stream):
    shuffled = stream.sort_values("amount").reset_index(drop=True)
    with pytest.raises(ValueError, match="Sort the file by time"):
        time_order.demand_order(shuffled)


def test_the_split_puts_every_training_row_first(stream):
    past, future = time_order.split_at_day(stream, 80)
    assert past["day"].max() < future["day"].min()


def test_a_cutoff_that_empties_one_side_is_refused(stream):
    with pytest.raises(ValueError, match="empty"):
        time_order.split_at_day(stream, 9999)
