# Professor Wiring Plan

Status: implementation branch `professor-wiring-v2`.

## Preservation rule

The Professor is added alongside the existing DATA-MIND 2.4 Mathematician. It does not replace, rename, bypass, or weaken the Mathematician, its append-only memory, shortcut learner, controller, inverse-child revision, checkpoint/rollback machinery, or the verifier boundary.

## Role separation

- Professor: evaluates proof-search progress and emits bounded partial-credit / penalty signals only.
- Mathematician: learns from persistent experience and optimizes legal search-control knobs.
- Rotation / inverse child: basin-escape mechanism when ordinary optimization stalls.
- Verifier: sole authority for mathematical certification and BANK commitment.

## Objective

Let `R(s) in [0,1]` be positive progress reward and `P(s) in [0,1]` be bounded penalty. For fixed `lambda >= 0`, define

`C(s) = (R(s) + lambda * (1 - P(s))) / (1 + lambda)`

and

`H(s) = 1 - C(s)`.

The Professor exposes bounded grading information such as `C` or `H`; it never exposes hidden proof steps, the next inference, or certificate content. The Mathematician may use that grading signal as an additional optimization input.

## Gating

Architecture is fixed; experiments vary activation gates. Professor and Mathematician receive independent gates so either can be ablated without deleting the other. Verifier certification is never gated off for scientific acceptance.

Initial gates to support:

- `professor_enabled`
- `mathematician_enabled`
- `rotation_enabled`
- `professor_to_mathematician_enabled`

Later wiring may add independent gates for Counselor, Creativity, Dreamer/Simulator, Learning, and their edges without removing existing modules.

## First implementation target

1. Add a read-only Professor grading interface.
2. Keep DATA-MIND 2.4 behavior bit-for-bit equivalent when `professor_enabled=false`.
3. Feed Professor grade into Mathematician control only when both Professor and the Professor->Mathematician edge are enabled.
4. Log Professor grades and disagreements with existing quality metrics instead of silently overriding either signal.
5. Preserve verifier sovereignty and existing transaction provenance.
