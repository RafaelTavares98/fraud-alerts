"""Refuses a stream that is not in time order.

Everything downstream assumes that row 10 happened after row 9. A file
sorted by customer, or by amount, silently breaks every history feature
and every window, and the scores still look fine.
"""


def demand_order(frame, day="day"):
    """Returns the frame, or names the first row that goes backwards."""
    days = frame[day].to_list()
    for position in range(1, len(days)):
        if days[position] < days[position - 1]:
            raise ValueError(
                f"row {position} is dated day {days[position]}, after a row "
                f"dated day {days[position - 1]}. Sort the file by time."
            )
    return frame


def split_at_day(frame, cutoff, day="day"):
    """Everything before the cutoff trains, everything after is scored."""
    past = frame[frame[day] < cutoff]
    future = frame[frame[day] >= cutoff]
    if past.empty or future.empty:
        raise ValueError(f"day {cutoff} leaves one of the two sides empty")
    return past, future
