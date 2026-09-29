"""One model, fitted and scored, with nothing hidden."""

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def fit(features, target):
    _demand_both_outcomes(target)
    scaler = StandardScaler().fit(features)
    engine = LogisticRegression(max_iter=1000, class_weight="balanced")
    engine.fit(scaler.transform(features), target)
    return {"scaler": scaler, "engine": engine}


def score(fitted, features):
    scaled = fitted["scaler"].transform(features)
    return fitted["engine"].predict_proba(scaled)[:, 1]


def _demand_both_outcomes(target):
    if target.nunique() < 2:
        raise ValueError(
            "the training rows hold no fraud at all, so nothing can be learned"
        )
