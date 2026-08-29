#!/usr/bin/env python3
"""Run one professional ATP on one positive R01 Ocean instance and audit any proof.

The ATP sees only the positive TPTP problem.  A theorem-like status is not
scored as PROVED unless the frozen strict Ocean audit can reconstruct a
source-to-target path using only named input edge axioms exposed inside the
ATP's proof output block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def parse_time_file(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    text = path.read_text(encoding='utf-8', errors='replace')
    for line in text.splitlines():
        z = line.strip()
        if z.startswith('Maximum resident set size (kbytes):'):
            try:
                out['max_rss_kb'] = int(z.split(':', 1)[1].strip())
            except ValueError:
                pass
        elif z.startswith('Elapsed (wall clock) time'):
            out['time_v_elapsed'] = z.split(': ', 1)[1].strip() if ': ' in z else z
    return out


def status_from_output(solver: str, text: str, rc: int, timed_out: bool) -> str:
    if timed_out:
        return 'TIMEOUT'
    if re.search(r'SZS status\s+(Theorem|Unsatisfiable)', text, re.I):
        return 'THEOREM_CLAIM'
    if solver == 'SPASS' and re.search(r'Proof found', text, re.I):
        return 'THEOREM_CLAIM'
    if re.search(r'SZS status\s+(GaveUp|Unknown|Timeout|ResourceOut|MemoryOut)', text, re.I):
        return 'BOUNDED_UNKNOWN'
    if rc != 0:
        return 'FAULT'
    return 'UNKNOWN_OUTPUT'


def solver_command(name: str, problem: Path, limit_s: int) -> list[str]:
    if name == 'Vampire':
        return [os.environ['VAMPIRE_BIN'], '--mode', 'casc', '-t', str(limit_s), '-p', 'tptp', str(problem)]
    if name == 'E':
        return [os.environ['EPROVER_BIN'], '--auto', f'--cpu-limit={limit_s}', '--proof-object', str(problem)]
    if name == 'SPASS':
        return ['SPASS', '-TPTP=2', f'-TimeLimit={limit_s}', '-DocProof=1', str(problem)]
    if name == 'Prover9':
        return [os.environ['PROVER9_BIN'], '-tptp', '-tptp_out', '-t', str(limit_s), '-f', str(problem)]
    raise ValueError(name)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--solver', choices=['Vampire', 'E', 'SPASS', 'Prover9'], required=True)
    ap.add_argument('--problem', required=True)
    ap.add_argument('--audit-script', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--time-limit', type=int, default=150)
    ap.add_argument('--outer-grace', type=int, default=15)
    a = ap.parse_args()

    problem = Path(a.problem)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / 'solver.out'
    time_path = out / 'time_v.txt'
    audit_path = out / 'strict_audit.json'
    result_path = out / 'result.json'

    cmd = solver_command(a.solver, problem, a.time_limit)
    timed_out = False
    t0 = time.perf_counter()
    wrapped = ['/usr/bin/time', '-v', '-o', str(time_path)] + cmd
    try:
        cp = subprocess.run(
            wrapped,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=a.time_limit + a.outer_grace,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        rc = cp.returncode
        text = cp.stdout
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc = 124
        text = exc.stdout if isinstance(exc.stdout, str) else ''
    wall = time.perf_counter() - t0
    raw_path.write_text(text, encoding='utf-8', errors='replace')

    preliminary = status_from_output(a.solver, text, rc, timed_out)
    audit = None
    final_status = preliminary
    certificate_verified = False
    proof_length = None

    if preliminary == 'THEOREM_CLAIM':
        acp = subprocess.run(
            [
                os.environ.get('PYTHON', 'python'),
                a.audit_script,
                '--problem', str(problem),
                '--output', str(raw_path),
                '--out', str(audit_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,
            check=False,
        )
        if audit_path.exists():
            audit = json.loads(audit_path.read_text(encoding='utf-8'))
            certificate_verified = bool(audit.get('certificate_verified'))
            proof_length = audit.get('proof_length')
        if acp.returncode != 0:
            final_status = 'AUDIT_FAULT'
        elif certificate_verified:
            final_status = 'PROVED'
        else:
            final_status = 'UNVERIFIED_CLAIM'

    result = {
        'solver': a.solver,
        'status': final_status,
        'preliminary_status': preliminary,
        'certificate_verified': certificate_verified,
        'proof_length': proof_length,
        'wall_s': wall,
        'returncode': rc,
        'timed_out': timed_out,
        'time_limit_s': a.time_limit,
        'outer_grace_s': a.outer_grace,
        'problem_sha256': sha256_file(problem),
        'command': ' '.join(cmd),
        'strict_audit': audit,
        **parse_time_file(time_path),
    }
    result_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
