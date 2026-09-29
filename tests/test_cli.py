import pytest

from data import make_transactions
from fraud_alerts import cli


def written(tmp_path, rows):
    return str(make_transactions.write_csv(rows, tmp_path / "stream.csv"))


def test_the_threshold_command_prints_the_queue(tmp_path, rows, capsys):
    code = cli.main(
        ["threshold", written(tmp_path, rows), "--cutoff", "80", "--review-capacity", "200"]
    )
    printed = capsys.readouterr().out
    assert code == 0
    assert "Best threshold" in printed and "alerts a day" in printed


def test_the_word_accuracy_never_appears(tmp_path, rows, capsys):
    """It is the number that hides the whole problem here."""
    cli.main(["threshold", written(tmp_path, rows), "--cutoff", "80"])
    assert "accuracy" not in capsys.readouterr().out.lower()


def test_the_stream_command_returns_one_when_it_drifts(tmp_path, capsys):
    drifting = make_transactions.make_stream(
        12000, 120, seed=3, fraud_rate=0.02, drift_day=80
    )
    code = cli.main(
        [
            "stream", written(tmp_path, drifting),
            "--cutoff", "60", "--threshold", "0.5", "--label-delay", "20",
        ]
    )
    assert code == 1
    assert "DRIFT" in capsys.readouterr().out


def test_a_missing_column_stops_the_run(tmp_path, rows):
    with pytest.raises(ValueError, match="chargeback"):
        cli.main(
            ["threshold", written(tmp_path, rows), "--cutoff", "80", "--target", "chargeback"]
        )
