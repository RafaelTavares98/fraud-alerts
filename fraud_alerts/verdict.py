"""Turns the numbers into the sentence somebody has to act on."""


SHIP = "Ship this threshold, not the one with the best F1."
NO_ROOM = "Do not ship this model."
RETRAIN = "Retrain."
HOLDING = "Holding. No window has slipped."


def on_threshold(chosen):
    if chosen["chosen"] is None or chosen["reason"]:
        return {
            "verdict": NO_ROOM,
            "reason": _why_not(chosen),
        }
    best = chosen["chosen"]
    return {
        "verdict": SHIP,
        "reason": (
            f"It catches {best['caught']} of {best['frauds']} frauds inside a "
            f"queue of {best['alerts_a_day']:.0f} alerts a day."
        ),
    }


def on_drift(watched):
    slipped = [one for one in watched if one["drifted"]]
    if not slipped:
        return {"verdict": HOLDING, "reason": "Precision held across every window."}
    first = slipped[0]
    name, fallen = _what_fell(watched[0], first)
    return {
        "verdict": RETRAIN,
        "reason": (
            f"{name} fell {fallen:.0%} by window {first['window']}. The "
            "pattern the model learned is not the pattern arriving now."
        ),
    }


def _what_fell(start, slipped):
    """Names whichever of the two actually moved, not whichever is first."""
    drops = {
        "Precision": _drop(start["precision"], slipped["precision"]),
        "Recall": _drop(start.get("recall", 0), slipped.get("recall", 0)),
    }
    name = max(drops, key=drops.get)
    return name, drops[name]


def _drop(start, now):
    return (start - now) / start if start else 0.0


def _why_not(chosen):
    if chosen["chosen"] is None:
        return (
            "Every threshold sends more alerts than the team can read. Either "
            "the model is too weak or the queue is too small."
        )
    return (
        "The alerts cost more to review than the fraud they catch is worth. "
        "A person reading this queue loses money on every shift."
    )
