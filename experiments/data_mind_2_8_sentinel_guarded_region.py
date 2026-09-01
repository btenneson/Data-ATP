#!/usr/bin/env python3
"""Sentinel-guarded replay of DATA-MIND 2.8 signature computation.

Calibration is taken from a disjoint cohort slice immediately before the evaluation
region. Evaluation theorems are then processed one at a time. A theorem may be
quarantined without terminating the job when two signals agree: extreme elapsed
time relative to calibration and lack of stage progress. RSS is logged but is not
used as a kill signal here because ru_maxrss is process-cumulative on Linux.
"""
from __future__ import annotations

import argparse, csv, importlib.util, json, math, resource, signal, statistics, sys, time
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def med(xs):
    return float(statistics.median(xs))


def mad(xs):
    m = med(xs)
    return float(statistics.median(abs(x-m) for x in xs))


class SentinelQuarantine(Exception):
    pass


class CalibrationDeadline(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--ml-sic', required=True)
    ap.add_argument('--sanitizer', required=True)
    ap.add_argument('--atp-root', required=True)
    ap.add_argument('--old-ranker', required=True)
    ap.add_argument('--target', default='sgrpcl')
    ap.add_argument('--fraction', type=float, default=.95)
    ap.add_argument('--start', type=int, default=30001)
    ap.add_argument('--end', type=int, default=35000)
    ap.add_argument('--calibration-n', type=int, default=1000)
    ap.add_argument('--calibration-timeout-s', type=float, default=30.0)
    ap.add_argument('--sample-period-s', type=float, default=.25)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    db = Path(a.db).resolve(); atp_root = Path(a.atp_root).resolve()
    old_ranker = json.loads(Path(a.old_ranker).read_text())
    BASE = load_module('dm28_base_guard', Path(__file__).with_name('data_mind_2_8_train_proof_horizon95.py'))
    MLSIC = load_module('dm28_mlsic_guard', Path(a.ml_sic).resolve())
    SAN = load_module('dm28_san_guard', Path(a.sanitizer).resolve())

    full = MLSIC.parse_metamath(str(db), limit=None)
    target = full.nodes[a.target]
    ts = SAN.norm_statement(target.statement); tm = SAN.token_multiset_signature(ts)
    conv = SAN.top_level_converse(ts); tl = len(ts.split())
    exact=set(); mult=set(); converse=set(); near=set()
    for name, nd in full.nodes.items():
        if nd.kind != 'theorem': continue
        ns = SAN.norm_statement(nd.statement)
        if ns == ts: exact.add(name); continue
        if SAN.token_multiset_signature(ns) == tm: mult.add(name); continue
        if conv is not None and ns == conv: converse.add(name); continue
        nl=len(ns.split()); ratio=min(nl,tl)/max(1,max(nl,tl))
        if ratio >= .80 and SAN.jaccard_tokens(ns,ts) >= .90: near.add(name)
    excluded = SAN.descendants(full, {a.target}|exact|mult|converse|near)
    theorem_nodes=[nd for nd in sorted(full.nodes.values(), key=lambda z:z.order) if nd.kind=='theorem']
    admissible=[nd for nd in theorem_nodes if nd.name not in excluded]
    n_train=max(1,min(len(admissible)-1,int(math.floor(a.fraction*len(admissible)))))
    train=admissible[:n_train]
    ranker_names={n for n in old_ranker.get('order',{}) if n in full.nodes and full.nodes[n].kind=='theorem'}
    if {nd.name for nd in train} != ranker_names: raise RuntimeError('95% cohort drift')
    if a.end > len(train): raise SystemExit('evaluation range exceeds cohort')
    c0=max(1,a.start-a.calibration_n); c1=a.start-1

    sys.path.insert(0,str(atp_root))
    import metamath, setmm_grammar as G, predator_fast_parse as PFP
    mm=metamath.load(str(db),say=lambda _s:None); by_tc=G.build_grammar(mm); PFP.install(G)

    def full_signature(nd, stagebox):
        toks=nd.statement.split(); stagebox[0]='parse'
        tree=None if (not toks or toks[0] != '|-') else G.parse(toks[1:],'wff',by_tc)
        if tree is None: return 'parse_none'
        stagebox[0]='dependency_cost'; BASE.logical_dependency_cost(full,nd)
        stagebox[0]='exact_hash'; BASE.canonical_tree_hash(tree,'exact')
        stagebox[0]='skeleton_hash'; BASE.canonical_tree_hash(tree,'skeleton')
        stagebox[0]='shape_hash'; BASE.canonical_tree_hash(tree,'shape')
        stagebox[0]='done'; return 'ok'

    # Disjoint calibration region; labels from evaluation are not used.
    calibration=[]
    prior=signal.getsignal(signal.SIGALRM)
    def calib_alarm(_s,_f): raise CalibrationDeadline()
    signal.signal(signal.SIGALRM,calib_alarm)
    for pos in range(c0,c1+1):
        nd=train[pos-1]; box=['start']; t0=time.monotonic()
        signal.setitimer(signal.ITIMER_REAL,a.calibration_timeout_s)
        try:
            st=full_signature(nd,box)
            if st=='ok': calibration.append(time.monotonic()-t0)
        except CalibrationDeadline:
            pass
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
    if len(calibration) < max(50, int(.9*(c1-c0+1))):
        raise RuntimeError(f'insufficient clean calibration: {len(calibration)}')
    m=med(calibration); d=mad(calibration)
    # Very conservative: floor at 1 s and require ~50 MADs above typical.
    elapsed_threshold=max(1.0,m+50.0*max(d,1e-4))

    csvp=out/'per_theorem.csv'; jsonlp=out/'per_theorem.jsonl'
    fields=['position','name','status','stage','elapsed_s','rss_before_kb','rss_after_kb','sentinel_threshold_s','reason']
    counts={'ok':0,'parse_none':0,'quarantine':0,'error':0}
    quarantined=[]
    with csvp.open('w',newline='',encoding='utf-8') as cf, jsonlp.open('w',encoding='utf-8') as jf:
        cw=csv.DictWriter(cf,fieldnames=fields); cw.writeheader()
        for pos in range(a.start,a.end+1):
            nd=train[pos-1]; box=['start']; t0=time.monotonic(); last_stage='start'; stage_since=t0
            before=rss_kb(); reason=''; status='ok'
            def sentinel_alarm(_s,_f):
                nonlocal last_stage, stage_since
                now=time.monotonic(); stage=box[0]
                if stage != last_stage:
                    last_stage=stage; stage_since=now
                elapsed=now-t0; stalled=now-stage_since
                if elapsed >= elapsed_threshold and stalled >= elapsed_threshold:
                    raise SentinelQuarantine(f'joint time+stall anomaly at stage={stage}')
            signal.signal(signal.SIGALRM,sentinel_alarm)
            signal.setitimer(signal.ITIMER_REAL,a.sample_period_s,a.sample_period_s)
            try:
                status=full_signature(nd,box)
            except SentinelQuarantine as e:
                status='quarantine'; reason=str(e)
            except Exception as e:
                status='error'; reason=f'{type(e).__name__}: {e}'
            finally:
                signal.setitimer(signal.ITIMER_REAL,0)
            elapsed=time.monotonic()-t0; after=rss_kb(); counts[status]+=1
            row={'position':pos,'name':nd.name,'status':status,'stage':box[0],
                 'elapsed_s':f'{elapsed:.6f}','rss_before_kb':before,'rss_after_kb':after,
                 'sentinel_threshold_s':f'{elapsed_threshold:.6f}','reason':reason}
            cw.writerow(row); cf.flush(); jf.write(json.dumps(row,sort_keys=True)+'\n'); jf.flush()
            print(f"[SENTINEL] pos={pos} name={nd.name} status={status} stage={box[0]} elapsed={elapsed:.6f}s",flush=True)
            if status=='quarantine': quarantined.append(row)
    signal.signal(signal.SIGALRM,prior)
    summary={'status':'SENTINEL_REPLAY_COMPLETE','architecture_version':'2.8-experimental-sentinel',
             'changes_frozen_release':False,'frozen_95pct_cohort_verified':True,
             'calibration_range':[c0,c1],'evaluation_range':[a.start,a.end],
             'calibration_median_s':m,'calibration_mad_s':d,'sentinel_elapsed_threshold_s':elapsed_threshold,
             'decision_rule':'quarantine only when extreme elapsed time and same-stage stall both persist',
             'rss_note':'logged only; ru_maxrss is process-cumulative and is not used as a theorem-local kill signal',
             'counts':counts,'quarantined':quarantined}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return 0

if __name__=='__main__': raise SystemExit(main())
