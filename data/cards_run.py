"""Runs the queue sizing against the public credit card dataset.

284,807 real card payments over two days, 492 of them fraud, which is
0.17%. The columns are anonymised: V1 to V28 are the output of a PCA the
bank ran before releasing it, so nothing here can be read as "the hour"
or "the country". Amount and time survive.

That anonymity is the reason this file exists. The made-up stream proves
the code finds a rule that was written by hand. This one proves the same
code sizes a queue on data nobody invented.
"""

import sys
import urllib.request

import pandas

from fraud_alerts import model
from fraud_alerts import threshold_choice
from fraud_alerts import verdict


SOURCE = (
    "https://raw.githubusercontent.com/nsethi31/"
    "Kaggle-Data-Credit-Card-Fraud-Detection/master/creditcard.csv"
)
CAPACITY = 100
FRAUD_COST = 120.0
REVIEW_COST = 4.0


def main():
    frame = _load()
    days = 2
    half = len(frame) // 2
    past, future = frame.iloc[:half], frame.iloc[half:]
    columns = [name for name in frame.columns if name not in ("Class", "Time")]
    fitted = model.fit(past[columns], past["Class"])
    scores = model.score(fitted, future[columns])
    chosen = threshold_choice.choose(
        list(scores), list(future["Class"]), CAPACITY, days, FRAUD_COST, REVIEW_COST
    )
    _print(frame, chosen)
    return 0


def _load():
    print("downloading 100 MB of real card payments, this takes a minute")
    with urllib.request.urlopen(SOURCE) as answer:
        return pandas.read_csv(answer)


def _print(frame, chosen):
    best = chosen["chosen"]
    said = verdict.on_threshold(chosen)
    print(f"rows .................. {len(frame):,} payments")
    print(f"fraud rate ............ {frame['Class'].mean():.3%}")
    print(f"capacity .............. {CAPACITY} alerts a day")
    if best is None:
        print(f"verdict ............... {said['verdict']}")
        print(f"reason ................ {said['reason']}")
        return
    print(f"best threshold ........ {best['threshold']:.4f}")
    print(f"  alerts a day ........ {best['alerts_a_day']:.0f}")
    print(f"  precision ........... {best['precision']:.1%}")
    print(f"  recall .............. {best['recall']:.1%}")
    print(f"  caught .............. {best['caught']} of {best['frauds']}")
    print(f"  net ................. {best['net']:,.0f}")
    print(f"verdict ............... {said['verdict']}")


if __name__ == "__main__":
    sys.exit(main())
