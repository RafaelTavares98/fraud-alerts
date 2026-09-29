"""What one threshold does to the people who read the alerts."""


def at_threshold(scores, target, threshold, days=1, fraud_cost=0, review_cost=0):
    """Precision, recall, the size of the queue, and what it is worth."""
    alerted = [position for position, one in enumerate(scores) if one >= threshold]
    caught = sum(target[position] for position in alerted)
    frauds = sum(target)
    return {
        "threshold": threshold,
        "alerts": len(alerted),
        "alerts_a_day": len(alerted) / days,
        "caught": caught,
        "frauds": frauds,
        "precision": caught / len(alerted) if alerted else 0.0,
        "recall": caught / frauds if frauds else 0.0,
        "net": caught * fraud_cost - len(alerted) * review_cost,
    }
