import pandas

from fraud_alerts import features


TWO_CUSTOMERS = pandas.DataFrame(
    {
        "customer_id": ["a", "a", "a", "b"],
        "day": [1, 2, 3, 1],
        "hour": [12, 3, 12, 12],
        "amount": [100.0, 100.0, 500.0, 50.0],
        "country": ["BR", "BR", "PA", "BR"],
    }
)


def test_the_first_transaction_has_no_history_to_lean_on():
    built = features.build(TWO_CUSTOMERS)
    assert built["seen_before"].iloc[0] == 0
    assert built["times_the_usual"].iloc[0] == 1.0


def test_a_big_payment_shows_as_times_the_usual():
    built = features.build(TWO_CUSTOMERS)
    assert built["times_the_usual"].iloc[2] == 5.0


def test_the_night_and_the_country_are_flags():
    built = features.build(TWO_CUSTOMERS)
    assert list(built["is_night"]) == [0, 1, 0, 0]
    assert list(built["is_away"]) == [0, 0, 1, 0]


def test_one_customer_never_sees_another_customers_history():
    built = features.build(TWO_CUSTOMERS)
    assert built["seen_before"].iloc[3] == 0


def test_every_column_is_a_number(stream):
    assert all(features.build(stream).dtypes != object)
