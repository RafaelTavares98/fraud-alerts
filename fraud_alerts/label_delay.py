"""Hides the labels that would not have arrived yet.

A chargeback lands weeks after the payment. A model measured as though
the answer was known the same evening is being measured in a world that
does not exist, and it always looks better there.
"""


def usable(frame, today, delay_days, day="day"):
    """The rows whose verdict has had time to come back."""
    _demand_a_delay(delay_days)
    return frame[frame[day] <= today - delay_days]


def unusable(frame, today, delay_days, day="day"):
    """The rows still waiting for a verdict. Scoring them is guessing."""
    return frame[frame[day] > today - delay_days]


def demand_settled(frame, today, delay_days, day="day"):
    """Refuses to measure a window whose labels have not landed."""
    waiting = len(unusable(frame, today, delay_days, day))
    if waiting:
        raise ValueError(
            f"{waiting} of these rows are newer than the {delay_days} day "
            "label delay, so their outcome is not known yet"
        )
    return frame


def _demand_a_delay(delay_days):
    if delay_days < 0:
        raise ValueError(f"a delay of {delay_days} days runs backwards")
