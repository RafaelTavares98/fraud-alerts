"""Prints the two blocks a person reads in five seconds."""


def render_threshold(chosen, capacity, fraud_cost, review_cost, verdict):
    lines = [
        _row("Capacity", f"{capacity} alerts a day, {review_cost} each to review"),
        _row("Missed fraud", f"{fraud_cost} each"),
    ]
    best = chosen["chosen"]
    if best is None:
        lines.append(_row("Best threshold", "none fits"))
        return "\n".join(lines + _closing(verdict))
    lines += [
        _row("Best threshold", f"{best['threshold']:.4f}"),
        _indent("alerts a day", f"{best['alerts_a_day']:.0f}, inside capacity"),
        _indent("precision", f"{best['precision']:.1%}"),
        _indent("recall", f"{best['recall']:.1%}"),
        _indent("caught", f"{best['caught']} of {best['frauds']} frauds"),
        _indent("net", f"{best['net']:,.0f} against no model"),
    ]
    return "\n".join(lines + _closing(verdict))


def render_drift(watched, delay_days, verdict):
    lines = [
        _row(
            "Label delay",
            f"{delay_days} days, so the newest rows score nothing yet",
        )
    ]
    for window in watched:
        lines.append(
            _row(
                f"Window {window['window']}",
                f"precision {window['precision']:.1%}  "
                f"recall {window['recall']:.1%}"
                + ("   DRIFT" if window["drifted"] else "")
                + ("   too small to judge" if window["too_small"] else ""),
            )
        )
    return "\n".join(lines + _closing(verdict))


def _closing(verdict):
    return [_row("Verdict", verdict["verdict"]), _row("Reason", verdict["reason"])]


def _row(label, value):
    return f"{label} {'.' * max(1, 22 - len(label))} {value}"


def _indent(label, value):
    return f"  {label} {'.' * max(1, 20 - len(label))} {value}"
