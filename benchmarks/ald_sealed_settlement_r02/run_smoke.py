from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd):
    subprocess.run(cmd, check=True, cwd=HERE)


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="ald_r02_smoke_"))
    try:
        run([sys.executable, "generator.py", "--out", str(root), "--smoke"])
        gt = json.loads((root / "sealed" / "ground_truth.json").read_text())
        ok = 0
        rows = []
        for entry in gt["instances"]:
            problem = root / "public" / "instances" / entry["id"]
            claim = root / "claims" / (entry["id"] + ".json")
            audit = root / "audits" / (entry["id"] + ".json")
            claim.parent.mkdir(parents=True, exist_ok=True)
            audit.parent.mkdir(parents=True, exist_ok=True)
            run([sys.executable, "reference_ald.py", "--problem", str(problem), "--out", str(claim)])
            run([sys.executable, "verifier.py", "--problem", str(problem), "--claim", str(claim), "--out", str(audit)])
            c = json.loads(claim.read_text())
            a = json.loads(audit.read_text())
            match = a["status"] == "CERTIFIED" and a["logical_outcome"] == entry["truth"]
            rows.append({"id": entry["id"], "truth": entry["truth"], "claim": c["claim"], "status": a["status"], "match": match})
            ok += int(match)

        sample = root / "public" / "instances" / gt["instances"][0]["id"]

        bad_proof = root / "bad_proof.json"
        bad_proof.write_text(json.dumps({
            "claim": "PROVED",
            "certificate": {"literals": ["p(n999999)"], "axioms": ["u0"]}
        }))
        bad_audit = root / "bad_proof_audit.json"
        run([sys.executable, "verifier.py", "--problem", str(sample), "--claim", str(bad_proof), "--out", str(bad_audit)])
        bad_result = json.loads(bad_audit.read_text())

        fake_i = root / "fake_independence.json"
        fake_i.write_text(json.dumps({"claim": "INDEPENDENT", "model_C": {}, "model_not_C": {}}))
        fake_i_audit = root / "fake_independence_audit.json"
        run([sys.executable, "verifier.py", "--problem", str(sample), "--claim", str(fake_i), "--out", str(fake_i_audit)])
        fake_i_result = json.loads(fake_i_audit.read_text())

        unknown = root / "unknown.json"
        unknown.write_text(json.dumps({"claim": "UNKNOWN", "reason": "30-second budget expired"}))
        unknown_audit = root / "unknown_audit.json"
        run([sys.executable, "verifier.py", "--problem", str(sample), "--claim", str(unknown), "--out", str(unknown_audit)])
        unknown_result = json.loads(unknown_audit.read_text())

        guards_pass = (
            bad_result["status"] == "AUDIT_FAILURE" and
            fake_i_result["status"] == "AUDIT_FAILURE" and
            unknown_result["status"] == "BOUNDED_UNKNOWN" and
            unknown_result["logical_outcome"] is None
        )
        summary = {
            "instances": len(rows),
            "certified_correct": ok,
            "all_settlements_pass": ok == len(rows),
            "adversarial_guards_pass": guards_pass,
            "all_pass": ok == len(rows) and guards_pass,
            "rows": rows
        }
        print(json.dumps(summary, indent=2))
        if not summary["all_pass"]:
            raise SystemExit(1)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
