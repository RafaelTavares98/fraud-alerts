"""The only file that reads the command line."""

import argparse
import sys

from fraud_alerts import analysis
from fraud_alerts import report
from fraud_alerts import stream_intake


def main(argv=None):
    options = _read_options(argv)
    frame = stream_intake.read_stream(options.path, options.target)
    if options.command == "threshold":
        return _threshold(frame, options)
    return _stream(frame, options)


def _threshold(frame, options):
    result = analysis.pick_threshold(
        frame,
        options.target,
        options.cutoff,
        options.review_capacity,
        options.fraud_cost,
        options.review_cost,
    )
    print(
        report.render_threshold(
            result["chosen"],
            options.review_capacity,
            options.fraud_cost,
            options.review_cost,
            result["verdict"],
        )
    )
    return 0 if result["chosen"]["chosen"] and not result["chosen"]["reason"] else 1


def _stream(frame, options):
    result = analysis.watch_drift(
        frame, options.target, options.cutoff, options.threshold, options.label_delay
    )
    print(report.render_drift(result["watched"], options.label_delay, result["verdict"]))
    return 1 if any(one["drifted"] for one in result["watched"]) else 0


def _read_options(argv):
    parser = argparse.ArgumentParser(
        prog="fraud-alerts",
        description="Sizes the alert queue, then watches it slip.",
    )
    parser.add_argument("command", choices=["threshold", "stream"])
    parser.add_argument("path", help="the CSV of transactions, in time order")
    parser.add_argument("--target", default="is_fraud")
    parser.add_argument("--cutoff", type=int, required=True, help="train on days before this")
    parser.add_argument("--review-capacity", type=int, default=200)
    parser.add_argument("--fraud-cost", type=float, default=120.0)
    parser.add_argument("--review-cost", type=float, default=4.0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--label-delay", type=int, default=30)
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
