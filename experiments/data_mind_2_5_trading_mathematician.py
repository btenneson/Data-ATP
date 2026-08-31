#!/usr/bin/env python3
"""DATA-MIND 2.5: The Trading Mathematician.

2.5 is an additive overlay on DATA-MIND 2.4.  It registers rule<->axiom
presentation trades and the Trading Optimization Problem while preserving the
2.4 proof kernel, verifier boundary, append-only memory, P/R/I/C Couples,
controller, inverse revision, and rollback behavior.

No trade changes the live Metamath calculus merely because it was proposed.
The initial 2.5 implementation treats trades as presentation/search objects and
requires an independent proof adapter/certificate before they can affect BANK
mathematics.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

from data_atp.trading import RuleAxiomTrade, TradeStatus, induction_trade_example

HERE = Path(__file__).resolve().parent
V24_PATH = HERE / "data_mind_2_4_mathematician_shortcuts.py"
spec = importlib.util.spec_from_file_location("data_mind_24_for_25", V24_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {V24_PATH}")
V24 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V24
spec.loader.exec_module(V24)

EventType = V24.EventType
emit = V24.emit

TRADING_THEOREM = (
    "For a closure-equivalence-certified trade tau, selected inference rules "
    "may be redistributed into traded axioms while consequence closure is "
    "preserved. Untraded axioms and rules are retained."
)
COMPLETE_TRADE_COROLLARY = (
    "If every rule is validly traded and the resulting presentation has an "
    "empty rule set, inference-rule compliance is vacuous; deductive content "
    "has been absorbed into axiomatic status."
)
TRADING_OPTIMIZATION = (
    "Among certified consequence-equivalent presentations, choose a "
    "presentation minimizing measured proof-search cost."
)


@dataclass(frozen=True, slots=True)
class TradeConfig:
    enabled: bool
    ledger: Path
    spec_paths: tuple[Path, ...]


_TRADE_CONFIG: TradeConfig | None = None


def _status(value: str) -> TradeStatus:
    try:
        return TradeStatus(str(value).lower())
    except ValueError as exc:
        raise ValueError(f"unknown trade status: {value}") from exc


def load_trade_specs(paths: tuple[Path, ...]) -> tuple[RuleAxiomTrade, ...]:
    trades: list[RuleAxiomTrade] = [induction_trade_example()]
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("trades", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError(f"trade spec must be a list or {{'trades': [...]}}: {path}")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"trade entry must be an object: {path}")
            trades.append(
                RuleAxiomTrade(
                    rule_name=str(row["rule_name"]),
                    traded_axiom=str(row["traded_axiom"]),
                    status=_status(str(row.get("status", "proposed"))),
                    closure_equivalence_certificate=(
                        str(row["closure_equivalence_certificate"])
                        if row.get("closure_equivalence_certificate")
                        else None
                    ),
                    provenance=str(row.get("provenance", path)),
                )
            )
    return tuple(trades)


class TradingMathematicianController(V24.MathematicianController):
    architecture_version = "2.5"

    def __init__(self, *args, **kwargs):
        if _TRADE_CONFIG is None:
            raise RuntimeError("DATA-MIND 2.5 trade config missing")
        super().__init__(*args, **kwargs)
        self.trade_cfg = _TRADE_CONFIG
        self.trade_candidates = load_trade_specs(self.trade_cfg.spec_paths)
        self.verified_trade_candidates = tuple(
            trade for trade in self.trade_candidates if trade.activatable
        )

        theorem_records = (
            ("trading_theorem", TRADING_THEOREM),
            ("complete_trade_corollary", COMPLETE_TRADE_COROLLARY),
            ("trading_optimization_problem", TRADING_OPTIMIZATION),
        )
        for kind, statement in theorem_records:
            self.memory_store.append(
                problem_id=self.cfg.problem_id,
                run_id=self.cfg.run_id,
                kind=kind,
                shortcut_type="presentation",
                action={"statement": statement},
                tags=("data-mind-2.5", "trading", "theorem"),
                source="DATA-MIND 2.5",
            )

        for trade in self.trade_candidates:
            payload = {
                "rule_name": trade.rule_name,
                "traded_axiom": trade.traded_axiom,
                "status": trade.status.value,
                "closure_equivalence_certificate": trade.closure_equivalence_certificate,
                "activatable": trade.activatable,
                "provenance": trade.provenance,
                "live_kernel_modified": False,
                "independent_verification_required": True,
            }
            V24.append_jsonl(
                self.trade_cfg.ledger,
                {
                    "kind": "rule_axiom_trade_candidate",
                    "problem_id": self.cfg.problem_id,
                    "run_id": self.cfg.run_id,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    **payload,
                },
            )
            self.memory_store.append(
                problem_id=self.cfg.problem_id,
                run_id=self.cfg.run_id,
                kind="rule_axiom_trade_candidate",
                outcome=trade.status.value,
                shortcut_type="presentation",
                action=payload,
                tags=("data-mind-2.5", "trading", trade.status.value),
                source="DATA-MIND 2.5",
            )

        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "data_mind_2_5_trading_layer_registered",
            trade_candidates=len(self.trade_candidates),
            closure_equivalence_certified=len(self.verified_trade_candidates),
            proof_kernel_changed=False,
            verifier_sovereign=True,
        )

    def summary(self) -> dict[str, Any]:
        data = super().summary()
        data.update(
            {
                "architecture_version": "2.5",
                "architecture_name": "DATA-MIND 2.5 The Trading Mathematician",
                "inherits_data_mind_2_4": True,
                "trading_theorem_registered": True,
                "complete_trade_corollary_registered": True,
                "trading_optimization_registered": True,
                "presentation_trading_enabled": self.trade_cfg.enabled,
                "trade_candidates": len(self.trade_candidates),
                "closure_equivalence_certified_trade_candidates": len(
                    self.verified_trade_candidates
                ),
                "untraded_rules_preserved": True,
                "existing_axioms_preserved": True,
                "original_2_4_overwritten": False,
                "trade_layer_modifies_live_metamath_kernel": False,
                "trade_candidates_require_proof_adapter_before_bank_use": True,
                "verifier_sovereign": True,
            }
        )
        return data


def main() -> int:
    global _TRADE_CONFIG
    custom = argparse.ArgumentParser(add_help=False)
    custom.add_argument("--version", choices=["2.5"], default="2.5")
    custom.add_argument("--trade-spec", action="append", default=[])
    custom.add_argument("--trade-ledger")
    custom.add_argument("--disable-trading", action="store_true")
    ours, remaining = custom.parse_known_args(sys.argv[1:])

    summary_raw = V24.arg_value(remaining, "--summary")
    if not summary_raw:
        raise SystemExit("2.5 requires the inherited base --summary path")
    summary_path = Path(summary_raw).resolve()
    _TRADE_CONFIG = TradeConfig(
        enabled=not ours.disable_trading,
        ledger=(
            Path(ours.trade_ledger).resolve()
            if ours.trade_ledger
            else summary_path.with_name("trading_runtime_ledger.jsonl")
        ),
        spec_paths=tuple(Path(p).resolve() for p in ours.trade_spec),
    )

    # Rebind only the 2.4 module's controller symbol.  The 2.4 source file and
    # architecture remain unchanged on disk and in history.
    V24.MathematicianController = TradingMathematicianController
    original_argv = sys.argv[:]
    sys.argv = [original_argv[0], "--version", "2.4", *remaining]
    try:
        rc = int(V24.main() or 0)
    finally:
        sys.argv = original_argv

    if summary_path.exists():
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        data.update(
            {
                "solver": "DATA-MIND 2.5 The Trading Mathematician",
                "architecture_version": "2.5",
                "inherits_data_mind_2_4": True,
                "trading_runtime_ledger": str(_TRADE_CONFIG.ledger),
                "trading_theorem": TRADING_THEOREM,
                "complete_trade_corollary": COMPLETE_TRADE_COROLLARY,
                "trading_optimization_problem": TRADING_OPTIMIZATION,
                "proof_kernel_unchanged": True,
                "candidate_still_requires_independent_verification": True,
            }
        )
        summary_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
