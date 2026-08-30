from __future__ import annotations

import json
from pathlib import Path

from data_atp.mathematician_memory import AppendOnlyMemoryStore, ShortcutLearner


KNOBS = ("x", "y")


def test_append_only_store_preserves_success_and_failure(tmp_path: Path) -> None:
    path = tmp_path / "memory.jsonl"
    store = AppendOnlyMemoryStore(path)
    success = store.append(
        problem_id="A",
        run_id="r1",
        kind="shortcut_outcome",
        outcome="success",
        shortcut_type="control",
        state_signature={"stale": 100},
        action={"delta": {"x": 0.1}},
    )
    failure = store.append(
        problem_id="A",
        run_id="r1",
        kind="shortcut_outcome",
        outcome="failure",
        shortcut_type="control",
        state_signature={"stale": 110},
        action={"delta": {"x": 0.2}},
    )
    assert success["record_id"] != failure["record_id"]
    assert store.verify()
    reloaded = AppendOnlyMemoryStore(path)
    assert reloaded.verify()
    assert [r["outcome"] for r in reloaded.records()] == ["success", "failure"]
    assert not hasattr(reloaded, "delete")


def test_failure_becomes_negative_shortcut_evidence(tmp_path: Path) -> None:
    store = AppendOnlyMemoryStore(tmp_path / "memory.jsonl")
    store.append(
        problem_id="A",
        run_id="r1",
        kind="shortcut_outcome",
        outcome="failure",
        shortcut_type="control",
        state_signature={"stale": 100},
        action={"delta": {"x": 0.1, "y": -0.05}},
        tags=("shortcut", "control"),
    )
    learner = ShortcutLearner(store, knobs=KNOBS, seed=1, distant_probability=0.0)
    proposal = learner.propose(
        problem_id="A",
        state_signature={"stale": 100},
        max_abs_delta=0.2,
        top_k_per_couple=4,
    )
    assert proposal.delta["x"] < 0.0
    assert proposal.delta["y"] > 0.0


def test_cross_problem_memory_is_retrievable(tmp_path: Path) -> None:
    store = AppendOnlyMemoryStore(tmp_path / "memory.jsonl")
    record = store.append(
        problem_id="OCEAN",
        run_id="old",
        kind="adult_control_observation",
        outcome="success",
        state_signature={"stale": 5000, "duplicate_rate": 0.4},
        action={"latent_delta": {"x": -0.02}},
        tags=("control", "shortcut"),
    )
    retrieved = store.retrieve(
        problem_id="SEMIGROUP",
        state_signature={"stale": 5000, "duplicate_rate": 0.4},
        top_k=5,
        distant_probability=0.0,
    )
    assert any(item[1]["record_id"] == record["record_id"] for item in retrieved)


def test_transaction_import_is_deduplicated(tmp_path: Path) -> None:
    tx_path = tmp_path / "transactions.jsonl"
    tx_path.write_text(
        json.dumps(
            {
                "sequence": 0,
                "event_type": "SelfReportFiled",
                "payload": {
                    "kind": "child_excursion_failed_evaluation",
                    "quality": 2.0,
                    "stale": 7000,
                },
                "digest": "abc",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    store = AppendOnlyMemoryStore(tmp_path / "memory.jsonl")
    first = store.ingest_transaction_log(tx_path, problem_id="A", run_id="old")
    second = store.ingest_transaction_log(tx_path, problem_id="A", run_id="old")
    assert first == 1
    assert second == 0
    assert store.records()[0]["outcome"] == "failure"
