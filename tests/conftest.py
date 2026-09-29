import pandas
import pytest

from data import make_transactions


@pytest.fixture
def rows():
    return make_transactions.make_stream(
        transactions=12000, days=120, seed=3, fraud_rate=0.02
    )


@pytest.fixture
def stream(rows):
    return pandas.DataFrame(rows)


@pytest.fixture
def drifting():
    return pandas.DataFrame(
        make_transactions.make_stream(
            transactions=12000, days=120, seed=3, fraud_rate=0.02, drift_day=80
        )
    )
