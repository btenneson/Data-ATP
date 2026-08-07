"""Reboot-resumable Data-ATP bridge for a Predator 8.004 search.

Phase 0.0.1 deliberately supports one Predator agent.  The frozen external
bundle is never edited.  Data-ATP supplies the durable transaction ledger,
full frontier checkpoints, exact expansion accounting, deterministic replay,
and human breadcrumbs around the external proof-search engine.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import heapq
import importlib.util
import json
import math
import os
from pathlib import Path
import pickle
import random
import subprocess
import sys
import tempfile
import time
from typing import Any

from .checkpoint import CheckpointError, CheckpointManager
from .events import EventType, TransactionLog


BRIDGE_VERSION = "0.1"
ENGINE_MODULE_NAME = "data_atp_external_predator_engine"
SEARCH_MODULE_NAME = "data_atp_external_predator_search"


class BridgeError(RuntimeError):
    """Raised when faithful continuation cannot be guaranteed."""


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.",
            suffix=".tmp", delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name is not None and os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write(
        path,
        (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False,
                    default=str) + "\n").encode("utf-8"),
    )


def load_module(name: str, path: Path):
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BridgeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    # Stable identity is required for pickled Node and Step instances.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def local_iso() -> str:
    return datetime.now().astimezone().isoformat()


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ps_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


class Continuation:
    def __init__(
        self,
        run_root: Path,
        run_id: str,
        identity: dict[str, Any],
        budget: int,
        checkpoint_every: int,
        resume: bool,
        argv_without_resume: list[str],
    ) -> None:
        self.run_root = run_root
        self.run_id = run_id
        self.identity = identity
        self.budget = int(budget)
        self.checkpoint_every = int(checkpoint_every)
        self.resume = bool(resume)
        self.argv_without_resume = list(argv_without_resume)

        self.logs = run_root / "logs"
        self.checkpoints = run_root / "checkpoints"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.checkpoints.mkdir(parents=True, exist_ok=True)
        self.breadcrumb_path = self.logs / "breadcrumbs.log"
        self.transaction_path = self.logs / "transactions.jsonl"
        self.continuation_path = run_root / "RUN_CONTINUATION.json"

        self.log = TransactionLog(self.transaction_path)
        self.manager = CheckpointManager(self.checkpoints, run_id, self.log)
        self.restored_state: dict[str, Any] | None = None
        self.replay_events = []
        self.replay_cursor = 0
        self.last_checkpoint_expansion = -1

    def breadcrumb(self, tag: str, text: str) -> None:
        with self.breadcrumb_path.open("a", encoding="utf-8", newline="\n") as h:
            h.write(f"\n{local_iso()} [{tag}]\nUTC: {utc_iso()}\n")
            h.write(text.rstrip() + "\n")
            h.flush()
            os.fsync(h.fileno())

    def resume_command(self) -> str:
        src = Path(__file__).resolve().parents[1]
        argv = [sys.executable, "-m", "data_atp.predator_bridge",
                *self.argv_without_resume, "--resume"]
        return (
            f"$env:PYTHONPATH = {ps_quote(str(src))}; & "
            + subprocess.list2cmdline(argv)
        )

    def write_continuation(
        self,
        status: str,
        expansion: int,
        checkpoint_path: str | None = None,
        checkpoint_sha: str | None = None,
        state_path: str | None = None,
        state_sha: str | None = None,
        note: str | None = None,
    ) -> None:
        payload = {
            "schema_version": BRIDGE_VERSION,
            "run_id": self.run_id,
            "status": status,
            "updated_local": local_iso(),
            "updated_utc": utc_iso(),
            "budget": self.budget,
            "expansions_consumed": int(expansion),
            "expansions_remaining": max(0, self.budget - int(expansion)),
            "last_valid_checkpoint": checkpoint_path,
            "last_valid_checkpoint_sha256": checkpoint_sha,
            "binary_state": state_path,
            "binary_state_sha256": state_sha,
            "transaction_log": str(self.transaction_path),
            "transaction_log_head": self.log.last_digest,
            "identity": self.identity,
            "resume_command": self.resume_command(),
        }
        if note:
            payload["note"] = note
        atomic_json(self.continuation_path, payload)

    def expansion_events(self):
        return [
            tx for tx in self.log.events(EventType.ACTION_EXECUTED)
            if tx.payload.get("kind") == "search_expansion_commit"
            and tx.payload.get("run_id") == self.run_id
        ]

    def durable_head(self) -> int:
        events = self.expansion_events()
        return int(events[-1].payload["expansion"]) if events else 0

    def save(self, state: dict[str, Any], expansion: int, reason: str) -> None:
        blob = pickle.dumps(state, protocol=pickle.HIGHEST_PROTOCOL)
        state_sha = hashlib.sha256(blob).hexdigest().upper()
        state_path = self.checkpoints / (
            f"search-state-{int(expansion):09d}-{time.time_ns()}.pkl"
        )
        atomic_write(state_path, blob)
        atomic_write(
            state_path.with_suffix(state_path.suffix + ".sha256"),
            (state_sha + "\n").encode("ascii"),
        )
        rel = str(state_path.relative_to(self.run_root))
        manifest = self.manager.save(
            {
                "bridge_version": BRIDGE_VERSION,
                "identity": self.identity,
                "budget": self.budget,
                "expansion": int(expansion),
                "state_path": rel,
                "state_sha256": state_sha,
                "transaction_log_head_before_checkpoint": self.log.last_digest,
                "reason": reason,
            },
            metadata={"bridge": "Predator 8.004", "reason": reason},
        )
        self.last_checkpoint_expansion = int(expansion)
        self.write_continuation(
            "RUNNING", expansion,
            manifest.checkpoint_path, manifest.sha256,
            str(state_path), state_sha, reason,
        )
        self.breadcrumb(
            "CHECKPOINT",
            "\n".join([
                f"Reason: {reason}",
                f"Committed expansion: {expansion}",
                f"Checkpoint: {manifest.checkpoint_path}",
                f"Checkpoint SHA-256: {manifest.sha256}",
                f"Binary state: {state_path}",
                f"Binary state SHA-256: {state_sha}",
                f"Transaction-log head: {self.log.last_digest}",
            ]),
        )

    def restore(self) -> dict[str, Any]:
        payload = self.manager.restore()
        snap = payload["snapshot"]
        if snap.get("bridge_version") != BRIDGE_VERSION:
            raise BridgeError("checkpoint bridge version mismatch")
        if snap.get("identity") != self.identity:
            raise BridgeError("checkpoint identity/configuration mismatch")
        if int(snap.get("budget", -1)) != self.budget:
            raise BridgeError("checkpoint budget mismatch")

        state_path = Path(str(snap["state_path"]))
        if not state_path.is_absolute():
            state_path = self.run_root / state_path
        blob = state_path.read_bytes()
        actual = hashlib.sha256(blob).hexdigest().upper()
        if actual != str(snap["state_sha256"]).upper():
            raise BridgeError("binary checkpoint SHA-256 mismatch")
        state = pickle.loads(blob)

        checkpoint_exp = int(snap["expansion"])
        later = [
            tx for tx in self.expansion_events()
            if int(tx.payload["expansion"]) > checkpoint_exp
        ]
        expected = checkpoint_exp + 1
        for tx in later:
            got = int(tx.payload["expansion"])
            if got != expected:
                raise BridgeError(
                    f"noncontiguous durable expansion ledger: expected {expected}, got {got}"
                )
            expected += 1

        self.restored_state = state
        self.replay_events = later
        self.replay_cursor = 0
        self.last_checkpoint_expansion = checkpoint_exp
        head = int(later[-1].payload["expansion"]) if later else checkpoint_exp
        self.log.append(
            EventType.SELF_REPORT_FILED,
            {
                "kind": "search_resume",
                "run_id": self.run_id,
                "checkpoint_expansion": checkpoint_exp,
                "durable_head": head,
                "replay_count": len(later),
            },
        )
        self.breadcrumb(
            "RESUME",
            f"Restored expansion {checkpoint_exp}.\n"
            f"Durable expansion head: {head}.\n"
            f"Deterministic replay required: {len(later)} expansions.\n"
            "The committed expansion counter is not reset.",
        )
        return state

    def commit(self, expansion: int, frontier_size: int, open_goals: int) -> bool:
        payload = {
            "kind": "search_expansion_commit",
            "run_id": self.run_id,
            "expansion": int(expansion),
            "frontier_size": int(frontier_size),
            "open_goals": int(open_goals),
        }
        if self.replay_cursor < len(self.replay_events):
            expected = self.replay_events[self.replay_cursor].payload
            if int(expected["expansion"]) != int(expansion):
                raise BridgeError(
                    f"deterministic replay diverged: expected expansion "
                    f"{expected['expansion']}, got {expansion}"
                )
            self.replay_cursor += 1
            return self.replay_cursor == len(self.replay_events)
        self.log.append(EventType.ACTION_EXECUTED, payload)
        return False

    def should_checkpoint(self, expansion: int) -> bool:
        return (
            expansion > self.last_checkpoint_expansion
            and expansion % self.checkpoint_every == 0
        )


def make_resumable_prover(search_module, continuation: Continuation):
    prepare_legal = search_module.prepare_legal

    def prove_legal_first(
        engine, goal_tree, index, budget, max_depth, rank=None,
        say=print, progress=2000, max_open=6, profile=None,
        seed=0, shared_use=None, agent_name=None,
    ):
        if profile is None:
            profile = engine.Profile(
                "deterministic", 0.0, 0.0, 0.0, 0.0, 0.0, 48, 1.0
            )
        if shared_use is None:
            shared_use = defaultdict(int)
        agent_name = agent_name or profile.name

        state = continuation.restored_state
        continuation.restored_state = None
        if state is None:
            rng = random.Random(seed)
            local_use = defaultdict(int)
            start = engine.Node([(goal_tree, None, 0)], {}, (), 0)
            frontier = [(0.0, 0, start)]
            exp = tie = 0
            seen = set()
            diag = {
                "agent": agent_name, "budget": int(budget), "expansions": 0,
                "rough_closers": 0, "rough_openers": 0,
                "legal_closers": 0, "legal_openers": 0,
                "selected_candidates": 0, "children_pushed": 0,
                "frontier_max": 1, "states_pruned_depth": 0,
                "states_pruned_open_goals": 0, "states_duplicate": 0,
                "root": None,
            }
        else:
            if state["agent_name"] != agent_name:
                raise BridgeError("checkpoint agent/profile mismatch")
            frontier = state["frontier"]
            exp = int(state["exp"])
            tie = int(state["tie"])
            seen = state["seen"]
            rng = random.Random()
            rng.setstate(state["rng_state"])
            local_use = defaultdict(int, state["local_use"])
            shared_use.clear()
            shared_use.update(state["shared_use"])
            diag = dict(state["diag"])
            if state.get("terminal") == "proof_found":
                return state["result"], exp, diag

        def snapshot(terminal=None, result=None):
            return {
                "agent_name": agent_name,
                "frontier": frontier,
                "exp": exp,
                "tie": tie,
                "seen": seen,
                "rng_state": rng.getstate(),
                "local_use": dict(local_use),
                "shared_use": dict(shared_use),
                "diag": dict(diag),
                "terminal": terminal,
                "result": result,
            }

        if exp == 0 and continuation.last_checkpoint_expansion < 0:
            continuation.save(snapshot(), 0, "initial-search-state")

        t0 = time.perf_counter()

        def finish(open_goals: int) -> None:
            replay_finished = continuation.commit(exp, len(frontier), open_goals)
            if progress and say and exp % progress == 0:
                say(
                    "      [%s] %s committed expansions, %d open goals, %.0fs"
                    % (agent_name, f"{exp:,}", open_goals,
                       time.perf_counter() - t0)
                )
            if replay_finished:
                continuation.save(snapshot(), exp, "post-replay-compression")
            elif continuation.should_checkpoint(exp):
                continuation.save(snapshot(), exp, "periodic")

        while frontier and exp < budget:
            priority, _, node = heapq.heappop(frontier)
            exp += 1
            diag["expansions"] = exp

            if not node.goals:
                root = None
                for parent, ix, step in node.trail:
                    if parent is None:
                        root = step
                    else:
                        parent.subs[ix] = step
                result = (root, node.sub)
                finish(0)
                continuation.save(
                    snapshot("proof_found", result), exp, "proof-found"
                )
                return result, exp, diag

            if node.depth >= max_depth:
                diag["states_pruned_depth"] += 1
                finish(len(node.goals))
                continue
            if len(node.goals) > max_open:
                diag["states_pruned_open_goals"] += 1
                finish(len(node.goals))
                continue

            gi = engine.pick_goal(node.goals, node.sub)
            gt, slot, hix = node.goals[gi]
            rest = node.goals[:gi] + node.goals[gi + 1:]
            gt = engine.apply_sub(gt, node.sub)
            key = (
                node.depth,
                " ".join(gt.tokens()),
                tuple(sorted(
                    " ".join(engine.apply_sub(g, node.sub).tokens())
                    for g, _, _ in rest
                )),
            )
            if key in seen:
                diag["states_duplicate"] += 1
                finish(len(node.goals))
                continue
            seen.add(key)

            rough_closers, rough_openers = index.candidates(gt)
            legal_closers, prepared_c = prepare_legal(
                engine, gt, rough_closers, node.sub
            )
            legal_openers, prepared_o = prepare_legal(
                engine, gt, rough_openers, node.sub
            )
            prepared = {**prepared_c, **prepared_o}

            diag["rough_closers"] += len(rough_closers)
            diag["rough_openers"] += len(rough_openers)
            diag["legal_closers"] += len(legal_closers)
            diag["legal_openers"] += len(legal_openers)
            if diag["root"] is None:
                diag["root"] = {
                    "rough_closers": len(rough_closers),
                    "rough_openers": len(rough_openers),
                    "legal_closers": len(legal_closers),
                    "legal_openers": len(legal_openers),
                }
                if say:
                    say(
                        "      [%s] root candidates: rough %s closer / %s opener; "
                        "legal %s closer / %s opener"
                        % (agent_name, f"{len(rough_closers):,}",
                           f"{len(rough_openers):,}", f"{len(legal_closers):,}",
                           f"{len(legal_openers):,}")
                    )

            scores_c = rank(gt, legal_closers) if rank else [0.0] * len(legal_closers)
            scores_o = rank(gt, legal_openers) if rank else [0.0] * len(legal_openers)
            ranked_c = engine._candidate_scores(
                gt, legal_closers, scores_c, profile, rng, local_use, shared_use
            )
            ranked_o = engine._candidate_scores(
                gt, legal_openers, scores_o, profile, rng, local_use, shared_use
            )
            pick = ranked_c + engine._counterfactual_slice(
                ranked_o, profile.opener_cap, profile.exploration, rng
            )
            diag["selected_candidates"] += len(pick)

            for candidate_score, item in pick:
                label, _conclusion_tree, data = item
                mapping, substitution = prepared[label]
                _dvs, f_hyps, e_hyps, _conclusion = data
                fmap = {
                    variable: mapping.get(variable, engine.fresh(typecode))
                    for _, typecode, variable in f_hyps
                }
                for _, typecode, variable in f_hyps:
                    mapping.setdefault(variable, fmap[variable])
                step = engine.Step(label, fmap, data)
                newgoals = []
                ok = True
                for hypothesis_index, (_, statement) in enumerate(e_hyps):
                    try:
                        child = engine.G.parse(statement[1:], "wff", index.by_tc)
                    except (RecursionError, engine.MMError):
                        child = None
                    if child is None:
                        ok = False
                        break
                    newgoals.append((
                        engine.rename_apart(child, mapping),
                        step,
                        hypothesis_index,
                    ))
                if not ok:
                    continue
                local_use[label] += 1
                shared_use[label] += 1
                tie += 1
                guide = math.tanh(candidate_score / 2.0)
                edge_cost = (0.25 if not e_hyps else 1.0) - 0.20 * guide
                state_cost = 0.02 * len(newgoals + rest)
                heapq.heappush(
                    frontier,
                    (
                        priority + edge_cost + state_cost,
                        tie,
                        engine.Node(
                            newgoals + rest,
                            substitution,
                            node.trail + ((slot, hix, step),),
                            node.depth + 1,
                        ),
                    ),
                )
                diag["children_pushed"] += 1
                diag["frontier_max"] = max(diag["frontier_max"], len(frontier))

            finish(len(node.goals))

        diag["frontier_exhausted"] = not frontier
        diag["budget_exhausted"] = exp >= budget
        continuation.save(snapshot("agent_finished"), exp, "agent-finished")
        return None, exp, diag

    return prove_legal_first


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Data-ATP Phase 0.0.1 resumable Predator 8.004 bridge"
    )
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--run-id", default="Data-ATP-run-001")
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--environment", required=True)
    ap.add_argument("--engine", default="Predator_8.001_FROZEN.py")
    ap.add_argument("--label", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--budget", type=int, default=80000)
    ap.add_argument("--max-depth", type=int, default=10)
    ap.add_argument("--agents", type=int, default=1)
    ap.add_argument("--creativity", type=float, default=0.55)
    ap.add_argument("--seed", type=int, default=2301)
    ap.add_argument("--opener-cap", type=int, default=48)
    ap.add_argument("--max-open", type=int, default=6)
    ap.add_argument("--progress", type=int, default=2000)
    ap.add_argument("--checkpoint-every", type=int, default=2000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--resume", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    if a.agents != 1:
        raise SystemExit(
            "Phase 0.0.1 resumable bridge deliberately supports --agents 1 only"
        )
    if min(a.budget, a.max_depth, a.max_open, a.checkpoint_every) < 1:
        raise SystemExit("budget/depth/max-open/checkpoint-every must be positive")
    if not 0.0 <= a.creativity <= 1.0:
        raise SystemExit("creativity must be in [0,1]")

    run_root = Path(a.run_root).resolve()
    bundle = Path(a.bundle).resolve()
    environment = Path(a.environment).resolve()
    model = Path(a.model).resolve()
    engine_path = (bundle / a.engine).resolve()
    search_path = (bundle / "predator8_004_search.py").resolve()
    inventory = run_root / "code" / "external" / "Predator_8.004_SHA256SUMS.txt"
    for path in (bundle, environment, model, engine_path, search_path):
        if not path.exists():
            raise SystemExit(f"required path missing: {path}")

    if str(bundle) not in sys.path:
        sys.path.insert(0, str(bundle))
    search_module = load_module(SEARCH_MODULE_NAME, search_path)

    def stable_load_engine(path):
        return load_module(ENGINE_MODULE_NAME, Path(path).resolve())

    search_module.load_engine = stable_load_engine
    # Import engine/grammar classes before a resume unpickles frontier objects.
    stable_load_engine(engine_path)

    identity = {
        "run_id": a.run_id,
        "target": a.label,
        "budget": a.budget,
        "max_depth": a.max_depth,
        "agents": a.agents,
        "creativity": a.creativity,
        "seed": a.seed,
        "opener_cap": a.opener_cap,
        "max_open": a.max_open,
        "environment_sha256": sha256(environment),
        "model_sha256": sha256(model),
        "engine_sha256": sha256(engine_path),
        "search_driver_sha256": sha256(search_path),
        "external_inventory_sha256": sha256(inventory) if inventory.exists() else None,
        "bridge_sha256": sha256(Path(__file__).resolve()),
    }
    raw = list(argv if argv is not None else sys.argv[1:])
    raw_without_resume = [x for x in raw if x != "--resume"]
    cont = Continuation(
        run_root, a.run_id, identity, a.budget, a.checkpoint_every,
        a.resume, raw_without_resume,
    )

    if a.resume:
        try:
            cont.restore()
        except (CheckpointError, BridgeError, OSError, ValueError,
                pickle.UnpicklingError) as exc:
            raise SystemExit(f"resume refused: {exc}") from exc
    elif any(cont.checkpoints.glob("checkpoint-*.json")):
        raise SystemExit("checkpoints already exist; use --resume or a new run directory")

    search_module.prove_legal_first = make_resumable_prover(search_module, cont)

    predator_argv = [
        str(environment), "--engine", str(engine_path), "--label", a.label,
        "--model", str(model), "--budget", str(a.budget),
        "--max-depth", str(a.max_depth), "--agents", "1",
        "--creativity", str(a.creativity), "--seed", str(a.seed),
        "--opener-cap", str(a.opener_cap), "--max-open", str(a.max_open),
        "--progress", str(a.progress), "--out", str(Path(a.out).resolve()),
        "--report", str(Path(a.report).resolve()),
    ]

    cont.log.append(
        EventType.SELF_REPORT_FILED,
        {
            "kind": "search_resume" if a.resume else "search_launch",
            "run_id": a.run_id,
            "pid": os.getpid(),
            "identity": identity,
            "predator_argv": predator_argv,
        },
    )
    cont.breadcrumb(
        "RESUME" if a.resume else "LAUNCH",
        "\n".join([
            f"PID: {os.getpid()}", f"Target: {a.label}",
            f"Budget: {a.budget}", f"Seed: {a.seed}", "Agents: 1",
            f"Creativity: {a.creativity}", f"Max depth: {a.max_depth}",
            f"Opener cap: {a.opener_cap}", f"Max open: {a.max_open}",
            f"Checkpoint interval: {a.checkpoint_every}",
            f"Environment SHA-256: {identity['environment_sha256']}",
            f"Model SHA-256: {identity['model_sha256']}",
            f"Engine SHA-256: {identity['engine_sha256']}",
            f"Search driver SHA-256: {identity['search_driver_sha256']}",
            f"Data bridge SHA-256: {identity['bridge_sha256']}",
            f"Transaction log: {cont.transaction_path}",
            f"Checkpoint directory: {cont.checkpoints}",
            "External Predator files remain unmodified.",
        ]),
    )

    old_argv = sys.argv
    started = time.perf_counter()
    try:
        sys.argv = [str(search_path), *predator_argv]
        rc = int(search_module.main())
    except KeyboardInterrupt:
        head = cont.durable_head()
        cont.write_continuation(
            "INTERRUPTED", head,
            note="KeyboardInterrupt; resume from last durable expansion head.",
        )
        cont.breadcrumb(
            "INTERRUPT",
            f"Interrupted after durable expansion {head}.\n"
            "No mathematical result recorded. Use RUN_CONTINUATION.json.",
        )
        return 130
    except Exception as exc:
        head = cont.durable_head()
        cont.write_continuation(
            "ERROR", head, note=f"{type(exc).__name__}: {exc}"
        )
        cont.breadcrumb(
            "ERROR", f"{type(exc).__name__}: {exc}\nNo mathematical result inferred."
        )
        raise
    finally:
        sys.argv = old_argv

    elapsed = time.perf_counter() - started
    report_path = Path(a.report).resolve()
    report = {}
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    expansions = int(report.get("expansions", cont.durable_head()))
    outcome = str(report.get("outcome", "UNKNOWN"))
    status = "VERIFIED" if rc == 0 else outcome
    cont.write_continuation(
        status, expansions,
        note=f"External search exited {rc}; outcome={outcome}.",
    )
    cont.breadcrumb(
        "VERIFIED" if rc == 0 else ("UNKNOWN" if rc == 1 else "STOP"),
        f"External return code: {rc}\nOutcome: {outcome}\n"
        f"Expansions: {expansions}\nWall seconds this process: {elapsed:.3f}\n"
        f"Report: {report_path}",
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
