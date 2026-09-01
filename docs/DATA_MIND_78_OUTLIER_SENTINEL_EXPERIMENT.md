# DATA-MIND 78-Outlier Sentinel Experiment

## Purpose

Evaluate whether a defensive Sentinel can distinguish a pathological theorem-signature computation from expensive but valid computations without destroying useful training data.

The frozen evaluation region is cohort positions 30,001–35,000. Prior diagnostics identified 78 resource outliers in this region: 77 that completed and one pathological case known as `quartfull`.

This experiment is not a search for a threshold that kills all outliers. The target behavior is deliberately asymmetric:

- pass the 77 expensive-but-completing outliers;
- quarantine/stop `quartfull` before it can dominate memory or wall-clock resources;
- preserve ordinary cases;
- complete downstream learning when the protected pipeline is used.

## Non-negotiable anti-leakage rule

`quartfull` and the labels of the 78 evaluation cases MUST NOT be used to tune Sentinel thresholds. Sentinel parameters are fixed from the non-evaluation calibration population (or from a separately frozen calibration split) before scoring the 78 known cases.

## Arms

A. **Legacy control**: original signature/learner path, no Sentinel intervention. Diagnostic safeguards external to the process may still terminate a runaway job so infrastructure survives.

B. **Sentinel only**: Sentinel wraps full signature computation. The downstream learner is otherwise unchanged.

C. **Sentinel + defended learner**: the same frozen Sentinel wraps feature/signature computation, and the learner is the defended/tuned learner selected without using the 78 evaluation labels.

Arms B and C MUST use identical Sentinel parameters.

## Sentinel observations

For each theorem the runner records, where available:

- theorem/cohort identity;
- elapsed wall time;
- peak RSS / resident memory;
- RAM growth rate;
- progress or signature-growth rate;
- robust time anomaly score;
- robust memory anomaly score;
- joint anomaly decision;
- hard-safety decision, if any;
- final state: completed, quarantined, timed out, memory stopped, errored;
- detection latency and resource use at intervention.

A memory anomaly by itself is not sufficient grounds for quarantine. The experiment is specifically intended to test whether joint evidence (for example unusual time together with unusual RAM behavior and poor progress) separates `quartfull` from the 77 legitimate outliers.

## Default robust scoring

For a metric x with calibration median m and median absolute deviation MAD,

    robust_z(x) = 0.67448975 * (x - m) / MAD

When MAD is zero, the implementation fails conservatively to a neutral score rather than dividing by zero. The calibration statistics are immutable during the 78-case evaluation.

Sentinel policy has two layers:

1. **Hard infrastructure ceiling**: an absolute time or memory limit whose only purpose is preventing machine/job failure. This ceiling is reported separately and is not counted as an intelligent Sentinel classification.
2. **Adaptive quarantine rule**: a frozen joint-resource rule based on calibration statistics. A single high memory score does not trigger quarantine. Quarantine requires multiple independent warning signals or a specifically preregistered runaway condition.

Exact thresholds are written into the result manifest before evaluation begins.

## Primary endpoint

The primary endpoint is exact stress-set behavior:

    77/77 legitimate outliers complete
    AND
    quartfull is quarantined/stopped

This is reported separately for arms B and C.

## Secondary endpoints

- false-positive rate among the 77 legitimate outliers;
- false-positive rate over the full 30,001–35,000 region;
- quartfull detection latency;
- peak RAM saved relative to the legacy arm where measurable;
- wall-clock saved relative to the legacy arm where measurable;
- percentage of theorem signatures successfully produced;
- learner/training completion;
- downstream learner quality metrics chosen before evaluation;
- number and causes of hard-ceiling interventions.

## Failure conditions

The experiment is considered unsuccessful if any of the following occur:

- Sentinel is tuned after inspecting quartfull's evaluation behavior;
- all or most resource outliers are simply killed;
- a RAM-only outlier is automatically quarantined by definition;
- a quarantined case is silently converted to an ordinary negative training example;
- the protected learner receives partial/corrupt features as though they were complete;
- the result manifest cannot identify which rule caused each intervention.

Quarantined computations are censored/resource-pathology records, not theorem-status labels.

## Required artifacts

Each arm writes machine-readable per-theorem records plus a summary containing:

- code revision;
- cohort identity and ordering hash;
- Sentinel configuration hash;
- learner configuration hash;
- calibration population hash;
- counts of complete/quarantined/error cases;
- the 78-case confusion table;
- resource summaries;
- whether learner training completed.

## Interpretation

The strongest result is not merely that `quartfull` is stopped. It is that the same frozen policy stops `quartfull` while allowing all 77 previously observed expensive-but-valid outliers to survive. That would support Sentinel as a selective defensive layer rather than a disguised low timeout.

## Relationship to DATA-MIND architecture

Sentinel is a safety/control boundary around expensive feature/signature computation and learning. It is not a P/R/I/C reasoning agent, does not write mathematical facts to BANK, does not merge BANK with FUTUREBANK, and does not change verifier sovereignty. This experiment therefore isolates robustness of the learning substrate before broader module reactivation experiments.