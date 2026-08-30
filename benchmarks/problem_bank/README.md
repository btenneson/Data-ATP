# DATA MIND Running Problem Bank

This directory is the persistent problem bank for DATA MIND experiments.

The bank is intentionally reusable. A problem may be used in one experiment, reused in another, paired across versions, or reserved as a holdout at our discretion. Reuse is not considered a flaw; what matters is that exposure history is recorded accurately so we can distinguish learning, controlled comparison, and generalization.

## Permanent-memory rule

**Never delete successes or failures.**

For The Mathematician, experimental history is append-only evidence. Successful proofs, failed searches, rejected shortcuts, dead ends, verifier failures, timing failures, bad revisions, useful revisions, Couple communications, control decisions, and abandoned strategies should all remain available for later learning.

An old record may be reweighted, marked obsolete, superseded by a newer interpretation, or assigned very low retrieval priority, but it should not be erased from the learning history.

Conceptually, if the accumulated memory after experiment `t` is `M_t` and new evidence is `E_{t+1}`, then

\[
M_{t+1}=M_t \cup E_{t+1},
\]

not a replacement of `M_t` by only the currently successful material.

Failures are first-class learning data. A failed attempt can later become a negative shortcut, a dead-basin signature, a settlement-switch signal, a revision trigger, or a useful analogy for a different problem.

## Status classes

- `LAB` — freely reusable for development, debugging, tuning, ablations, and repeated learning experiments.
- `PAIRED` — intentionally reused across two or more experiments for direct controlled comparison.
- `HOLDOUT` — intentionally withheld when we want clean generalization evidence.
- `TARGET` — an active or planned research target; may later be assigned to LAB, PAIRED, or HOLDOUT for a particular experiment.

A single problem can change role over time. The ledger records the history rather than pretending an old exposure did not happen.

## Shortcut-learning use

For shortcut experiments, distinguish at least three kinds of shortcut:

1. **Local** — e.g. selecting a useful lemma or inference.
2. **Structural** — e.g. quotient first, change representation, introduce an invariant, alter proof decomposition.
3. **Settlement-switching** — evidence that search should move among P/R/I/C modes.

Whenever practical, record both shortcut-enabled and shortcut-disabled cost on the same problem so that shortcut gain can be estimated as

\[
G_{shortcut}=\frac{C_{baseline}}{C_{shortcut}}.
\]

The relevant cost can include expansions, wall time, verifier work, memory, and proof length.

## Exposure policy

For each problem, record:

- first-seen date,
- problem family,
- formal system / source,
- intended settlement mode(s) P/R/I/C,
- reuse status,
- experiments / DATA MIND versions that have seen it,
- shortcut exposure,
- verification result,
- notes.

A result on a reused problem is valid evidence of learning or architectural comparison. A result on an unexposed holdout is stronger evidence of generalization. These are different questions and should be reported separately.

## Current priority order

1. **Semigroup closure problem** — active target. Finish and verify before moving on.
2. **Halo(0) ≈ R** — next major target after semigroup.

See `problem_bank.csv` for the running ledger.
