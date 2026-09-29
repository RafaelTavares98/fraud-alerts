# fraud-alerts

Sizes the fraud alert queue to the people who have to read it, then
watches it slip.

A model catches 92% of the fraud. The two analysts who review alerts
receive four thousand a day, so nobody reviews anything and the fraud
goes through anyway. The catch rate was never the product. The queue
was.

```
fraud-alerts threshold transactions.csv --cutoff 80 --review-capacity 200 --fraud-cost 120 --review-cost 4
fraud-alerts stream    transactions.csv --cutoff 60 --threshold 0.5 --label-delay 20
```

## What it prints

The threshold comes from the capacity and the cost of being wrong:

```
Capacity .............. 200 alerts a day, 4.0 each to review
Missed fraud .......... 120.0 each
Best threshold ........ 0.5062
  alerts a day ........ 41, inside capacity
  precision ........... 15.2%
  recall .............. 86.4%
  caught .............. 241 of 279 frauds
  net ................. 22,580 against no model
Verdict ............... Ship this threshold, not the one with the best F1.
```

A precision of 15% would fail a job interview and pass a shift. Six in
seven alerts are a wasted review at four dollars each, and the model
still catches 241 frauds worth 120 each. The queue fits in a working
day. That is the whole trade, and F1 cannot see any of it.

Then the stream, one window at a time:

```
Label delay ........... 20 days, so the newest rows score nothing yet
Window 1 .............. precision 22.5%  recall 62.0%
Window 2 .............. precision 14.6%  recall 30.1%   DRIFT
Window 3 .............. precision 0.0%  recall 0.0%   DRIFT
Verdict ............... Retrain.
Reason ................ Recall fell 51% by window 2. The pattern the model learned is not the pattern arriving now.
```

## The three things this does that a notebook does not

**It refuses to score a window whose labels have not arrived.** A
chargeback lands weeks after the payment. A model measured as though the
answer were known the same evening is being measured in a world that
does not exist, and it always looks better there. `--label-delay` holds
the newest rows out of the measurement entirely.

**It watches the queue go quiet, not only go wrong.** Drift has two
shapes. The loud one is precision falling: the queue fills with rubbish.
The quiet one is the model simply not firing any more, while the fraud
carries on. Precision looks perfect on three alerts a day, so a watcher
that reads precision alone calls that healthy. This one reads recall as
well.

**It never prints accuracy.** At a fraud rate of 0.17%, answering
"nothing is fraud" is 99.83% accurate. Accuracy is not a weak metric
here, it is a lie. There is a test that fails if the word ever appears
in the output.

On AUROC and AUPRC: the popular claim that AUPRC is simply better under
imbalance was refuted by a NeurIPS 2024 paper, which also found the
claim is usually made with no citation at all. Neither curve is printed.
What is printed is the working point you would actually ship.

## Against real data

```
python -m data.cards_run
```

```
rows .................. 284,807 payments
fraud rate ............ 0.173%
capacity .............. 100 alerts a day
best threshold ........ 1.0000
  alerts a day ........ 30
  precision ........... 98.3%
  recall .............. 26.0%
  caught .............. 58 of 223
  net ................. 6,724
verdict ............... Ship this threshold, not the one with the best F1.
```

That is the public ULB credit card set: 284,807 real payments over two
days, 492 of them fraud. The columns are anonymised, so nothing can be
hand-tuned.

Read the recall. With only 100 reviews a day available, the best
possible answer catches a quarter of the fraud. No model tuning changes
that, because the limit is the review desk and not the model. A project
that reported 0.97 AUROC here would have told the client nothing they
could act on.

**One bug this dataset found.** The threshold search used to walk an
even grid from 0.01 to 0.99. On this data every useful cut sits above
0.99, so the search walked straight past all of them and reported that
no threshold fitted. The cuts are now taken from the scores themselves.
The made-up data never would have shown it.

## Installing and running

```
pip install -r requirements.txt
python -m data.make_files
python -m fraud_alerts.cli threshold data/transactions.csv --cutoff 80 --review-capacity 200
python -m fraud_alerts.cli stream data/transactions_drifting.csv --cutoff 60 --threshold 0.5 --label-delay 20
```

The first command writes the two example streams from fixed seeds, so
every block above comes back identical. They are not committed.

The input is one row per transaction, in time order:

```
transaction_id,customer_id,day,hour,amount,country,is_fraud
t0,k17,0,14,183.44,BR,0
t1,k92,0,3,1204.10,BR,1
```

The exit code is 1 when the queue cannot be made to fit, or when a
window has drifted, so it fits in a pipeline.

## The tests

```
python -m pytest
```

43 tests. None opens a network connection or a database. The interesting
ones:

* A file that is not in time order has to raise, naming the row.
* A window whose labels have not landed has to raise, not report a
  number that cannot exist.
* The planted drift has to be caught, and a steady stream has to be left
  alone. Both directions.
* A window with three alerts must not be accused of drift on precision
  alone, and must be accused when its recall collapses.
* A smaller review capacity has to move the threshold up.
* The word "accuracy" must not appear in the output.

## The made-up data

`data/make_transactions.py` invents a stream where fraud and ordinary
life overlap, because they do. Some honest people buy a fridge at two in
the morning. A rule with no overlap produces a model that scores 100%
and teaches nobody anything; the first version of this generator did
exactly that, and it was rewritten.

Half way through the second stream, the fraud changes shape: from one
large payment at night to a trickle of small payments from abroad. The
drift watch has to notice, and a watcher that has never seen real drift
has never been tested.

## What this is not

Not a real-time service, not a rules engine, not a case management tool.
It reads a file and prints two blocks.

One model, one target, no graph features, no uplift. It says who to
review, not what to do with them. Logistic regression on purpose: the
coefficients can be shown to a client, and on data this shape a forest
wins by a rounding error and explains nothing.
