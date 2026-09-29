"""Builds what the model looks at, from each customer's own past.

Every value here could have been computed the instant the transaction
arrived. Nothing looks at a later row, because in production there is no
later row yet.
"""

NIGHT = range(0, 6)


def build(frame):
    """One row per transaction, numbers only."""
    ordered = frame.copy()
    by_customer = ordered.groupby("customer_id")["amount"]
    average_so_far = by_customer.transform(
        lambda amounts: amounts.shift().expanding().mean()
    )
    ordered["seen_before"] = by_customer.transform(
        lambda amounts: amounts.shift().expanding().count()
    ).fillna(0)
    ordered["usual_amount"] = average_so_far.fillna(ordered["amount"])
    ordered["times_the_usual"] = ordered["amount"] / ordered["usual_amount"]
    ordered["is_night"] = ordered.get("hour", 12).isin(NIGHT).astype(int)
    ordered["is_away"] = (ordered.get("country", "BR") != "BR").astype(int)
    return ordered[
        ["amount", "times_the_usual", "seen_before", "is_night", "is_away"]
    ]
