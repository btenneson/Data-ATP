# DATA-MIND 2.4 — The Mathematician

DATA-MIND 2.4 adds a persistent shortcut-learning layer to the tightened DATA-MIND 2.3 controller. It deliberately preserves the existing proof kernel, Metamath rules, verifier boundary, 11-dimensional logit-product-group control, inverse child revision, and checkpoint/rollback behavior.

The new hypothesis is narrower and testable:

> Can DATA-MIND reuse prior successes **and prior failures**, including information from apparently unrelated problems, to reduce the cost of verified mathematical search?

## Permanent-memory rule

The Mathematician's experimental memory is append-only.

- Never delete a success.
- Never delete a failure.
- Never delete a rejected shortcut, verifier rejection, dead end, bad revision, timeout, or neutral observation merely because it was unhelpful at the time.
- Later evidence may reweight or supersede an older interpretation, but does not erase the original record.

The runtime memory is a SHA-256 hash-chained JSONL file. There is intentionally no deletion API in `AppendOnlyMemoryStore`.

## What is remembered

The 2.4 runner can ingest complete prior DATA-MIND transaction logs. Imported records preserve their source problem/run, event kind, outcome classification, state telemetry when available, agent/couple provenance when available, verifier result when available, and the original event payload.

New 2.4 runs additionally remember:

- adult control movements;
- each P/R/I/C Couple's shortcut deliberation;
- consensus shortcut proposals;
- actual bounded shortcut knob movements;
- measured next-window shortcut outcomes;
- censored proposals when an agent ends before evaluation;
- run exposure and summary provenance.

## P/R/I/C Couples in shortcut learning

The proof calculus is not changed. P/R/I/C are used as diverse shortcut-memory perspectives before BANK commitment:

- **P Couple (P1/P2):** emphasizes previously successful routes/control moves.
- **R Couple (R1/R2):** treats failures and dead ends as negative-shortcut evidence; a failed direction can become evidence to move away from that direction.
- **I Couple (I1/I2):** receives a higher probability of distant/cross-problem retrieval so apparently irrelevant prior information can be tested as an analogy.
- **C Couple (C1/C2):** gives extra negative weight to verifier-rejected evidence and positive weight to verifier-accepted evidence.

The four Couple proposals are combined into one bounded control delta. This delta can only change already-legal search-control coordinates. It cannot alter Metamath inference rules or certify a proof.

## Shortcut objective

For a prior applied shortcut with control displacement `delta`, the next control window measures improvement from proof-distance and quality telemetry. Success/failure is retained as training evidence for future proposals.

The long-term quantity of interest remains a controlled cost ratio such as

```text
G_shortcut = C(shortcuts disabled) / C(shortcuts enabled)
```

where cost can include expansions, wall time, verifier work, memory, and final proof length. A repeated/reused problem measures learning or architecture change; a deliberately unexposed problem measures generalization. Those claims should be reported separately.

## Cross-problem and distant retrieval

Memory retrieval scores similarity but does **not** forbid cross-problem evidence. The I Couple additionally gets occasional low-relevance sampling. This is intentional: an Ocean failure, semigroup control pattern, Halo attempt, or other past experiment may be irrelevant mathematically yet useful strategically or metacognitively.

A record must contain an actionable control delta (or recoverable before/after control state) before it directly changes knobs. Non-actionable records are still preserved for future extensions of the shortcut model.

## Verifier sovereignty

Shortcut learning controls **what to try**, never **what is true**.

A candidate emitted by DATA-MIND 2.4 is still only a proposal. Independent verification remains required before BANK admission. Memory records may be wrong, speculative, stale, or misleading without compromising mathematical validity, because they have no certificate authority.

## Runtime files

The runner produces or updates:

- `mathematician_memory.jsonl` — append-only persistent memory;
- `shortcut_runtime_ledger.jsonl` — proposal/outcome measurements;
- `exposure_runtime_ledger.jsonl` — run/problem exposure history;
- the normal DATA-MIND transaction log and summary.

To import earlier transaction histories, repeat:

```text
--ingest-transactions PROBLEM_ID::path/to/transactions.jsonl
```

A path without `PROBLEM_ID::` is treated as prior exposure to the current problem.

## Ablation

Use `--disable-shortcuts` to keep memory recording/retrieval infrastructure present while preventing the learned shortcut delta from changing the live search controls. This gives a same-version shortcut-off comparison.

Important controls include:

- `--shortcut-step` — maximum absolute learned control displacement per control sample;
- `--shortcut-min-confidence` — minimum consensus confidence required to apply a shortcut;
- `--shortcut-top-k` — memories examined per Couple;
- `--distant-probability` — probability of surfacing an additional distant memory.

These are intended for fine-tuning. The first experiments should keep them conservative and compare against the unchanged 2.3 base as well as the 2.4 shortcut-off ablation.

## Current target order

1. Finish and verify the semigroup (`sgrpcl`) target.
2. Then move to `Halo(0) ≈ R`, carrying the accumulated append-only memory forward while recording exactly which prior information was available.
