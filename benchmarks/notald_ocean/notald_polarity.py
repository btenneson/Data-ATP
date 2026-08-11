"""Wrong-polarity settlement rules for the NOTALD Ocean benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Settlement(str, Enum):
    REFUTED = "REFUTED"
    BOUNDED_UNKNOWN = "BOUNDED_UNKNOWN"
    RUNNING = "RUNNING"
    AUDIT_FAILURE = "AUDIT_FAILURE"
    CRITICAL_AUDIT_FAILURE = "CRITICAL_AUDIT_FAILURE"


@dataclass(frozen=True)
class Evidence:
    """Verified-certificate state for one frozen consistent Ocean instance."""

    prover_has_verified_not_T: bool = False
    refuter_has_verified_T: bool = False
    budget_exhausted: bool = False


def settle(evidence: Evidence) -> Settlement:
    """Settle NOTALD without treating search failure as logical evidence.

    For this benchmark family the base hypotheses are frozen as consistent and T_L is known,
    independently of the solver, to be derivable. Therefore:

    * R proving T_L is the expected conclusive outcome: REFUTED.
    * P proving NOT T_L is an audit failure.
    * both polarities carrying accepted certificates is a critical audit failure.
    * no conclusive certificate at the resource boundary is BOUNDED_UNKNOWN.
    """
    if evidence.prover_has_verified_not_T and evidence.refuter_has_verified_T:
        return Settlement.CRITICAL_AUDIT_FAILURE
    if evidence.prover_has_verified_not_T:
        return Settlement.AUDIT_FAILURE
    if evidence.refuter_has_verified_T:
        return Settlement.REFUTED
    if evidence.budget_exhausted:
        return Settlement.BOUNDED_UNKNOWN
    return Settlement.RUNNING


def normalized_refuter_target(native_theorem_symbol: str) -> str:
    """Expose the intended frozen classical normalization target.

    This helper does not charge an Ocean inference. The exact normalization convention must be
    frozen in protocol.json before a scored run.
    """
    return native_theorem_symbol
