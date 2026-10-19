#!/usr/bin/env python3
"""M* engineering automation runner. Audit existing code; do not manufacture scientific claims.

- Frozen 0.8 source integrity is checked before and after each run.
- Candidate runs in a copied temporary directory; it can never overwrite frozen 0.8.
- Searches and their certificate replay are distinct processes.
- Machine-generated records separate evidence, constraints and inference.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent
FROZEN=ROOT/'frozen_0_8'
DEFAULT_CANDIDATE=ROOT/'candidate_0_9'
MANIFEST=ROOT/'frozen_sha256.json'
RECEIPT_ARGS=[
    ('Horn PROVED','examples/horn_problem.json','examples/horn_result.json',None),
    ('SAT','examples/sat_problem.json','examples/sat_result.json',None),
    ('UNSAT','examples/unsat_problem.json','examples/unsat_result.json',None),
    ('Metamath PROVED','examples/metamath_problem.json','examples/metamath_result.json','legacy_mm/demo0_base.mm')
]

def sha(f):
    h=hashlib.sha256()
    with open(f,'rb') as r:
        for b in iter(lambda:r.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def verify_frozen():
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    expected=m['files']
    observed={p.relative_to(FROZEN).as_posix():sha(p) for p in FROZEN.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    changed=[f for f in expected.keys() & observed.keys() if expected[f]!=observed[f]]
    missing=sorted(expected.keys()-observed.keys())
    unexpected=sorted(observed.keys()-expected.keys())
    return {'pass':not(changed or missing or unexpected),'expected_files':len(expected),
            'missing':missing,'changed':sorted(changed),'unexpected':unexpected,
            'archive_sha256_at_package_creation':m['source_archive_sha256']}

def source_digest(directory):
    files=sorted(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc',))
    h=hashlib.sha256()
    for p in files:
        h.update(p.relative_to(directory).as_posix().encode('utf8')+b'\0')
        h.update(bytes.fromhex(sha(p)))
    return {'sha256':h.hexdigest(),'file_count':len(files)}

def run_command(label,cmd,work,timeout,commands):
    start=time.perf_counter()
    try:
        r=subprocess.run(cmd,cwd=work,capture_output=True,text=True,errors='replace',timeout=timeout,
                         env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'})
        entry={'label':label,'command':cmd,'exit_code':r.returncode,'pass':r.returncode==0,
               'wall_seconds':round(time.perf_counter()-start,5),'stdout':r.stdout[-25000:],
               'stderr':r.stderr[-25000:]}
    except subprocess.TimeoutExpired as exc:
        entry={'label':label,'command':cmd,'exit_code':None,'pass':False,'timeout':True,
               'wall_seconds':round(time.perf_counter()-start,5),
               'stdout':str(exc.stdout or '')[-3000:],'stderr':str(exc.stderr or '')[-3000:]}
    commands.append(entry)
    return entry

def analyze_test(entry):
    match=re.search(r'Ran\s+(\d+)\s+tests?',entry['stdout']+'\n'+entry['stderr'])
    entry['test_count']=int(match.group(1)) if match else None
    # M* 0.8 has 18 tests. A significantly reduced suite must be flagged.
    if entry['test_count'] is None or entry['test_count']<18:
        entry['pass']=False
        entry['test_count_gate']='FAILED: at least 18 tests required'
    else: entry['test_count_gate']='PASS'
    return entry

def pipeline(candidate_path,mode,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
    initial=verify_frozen()
    if not initial['pass']:raise RuntimeError('Frozen baseline integrity failure; refusing to run')
    candidate_path=Path(candidate_path).resolve()
    if not candidate_path.exists():raise FileNotFoundError(candidate_path)
    if candidate_path==FROZEN:raise ValueError('Candidate cannot be the frozen baseline folder')
    report={'format':'MSTAR-AUTOPILOT-0.1','created_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Reproducible local checks; no automatic proof of generality or speedup',
            'mode':mode,'python':sys.version,'frozen_integrity_before':initial,
            'frozen_manifest_sha256':sha(MANIFEST),
            'candidate_path':str(candidate_path),
            'candidate_source':source_digest(candidate_path),
            'baseline_source':source_digest(FROZEN),
            'checks':[], 'evidence':{},'scientific_gates':{}}
    with tempfile.TemporaryDirectory(prefix='mstar-autopilot-') as temp:
        temp=Path(temp)
        for name,source in [('baseline',FROZEN),('candidate',candidate_path)]:
            work=temp/name
            shutil.copytree(source,work,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            item={'source':name,'checks':[]}
            report['evidence'][name]=item
            for script in (['tests'] if name=='baseline' else ['tests','tests_optimized']):
                cmd=[sys.executable]
                if script=='tests_optimized':cmd+=['-O']
                cmd+=['-m','unittest','discover','-s','tests','-v']
                analyze_test(run_command(name+'/'+script,cmd,work,60,report['checks']))
            if name=='baseline' and mode=='quick':continue
            run_command(name+'/demo',[sys.executable,'run_demo.py'],work,60,report['checks'])
            for label,problem,receipt,db in RECEIPT_ARGS:
                cmd=[sys.executable,'verify_receipt.py',problem,receipt]
                if db:cmd+=['--database',db]
                run_command(name+'/receipt/'+label,cmd,work,60,report['checks'])
                if name=='candidate':
                    # Separate frozen checker gate: candidate cannot certify itself
                    # by silently weakening or changing core.verify.
                    frozen_work=temp/'baseline'
                    frozen_cmd=[sys.executable,str(frozen_work/'verify_receipt.py'),
                                str((work/problem).resolve()),str((work/receipt).resolve())]
                    if db:frozen_cmd+=['--database',str((frozen_work/db).resolve())]
                    run_command('candidate/frozen_checker/'+label,frozen_cmd,
                                frozen_work,60,report['checks'])
            if mode=='full':
                benchmark=run_command(name+'/benchmark',[sys.executable,'benchmark.py'],work,120,report['checks'])
                if benchmark['pass']:
                    try:
                        b=json.loads((work/'benchmark_results_08.json').read_text(encoding='utf8'))
                        item['benchmark']={'rows':b['rows'],'warning':b.get('warning'),'family':b.get('family')}
                        if [i['n'] for i in b['rows']] != [4,6,8,10,12,14,16]:
                            benchmark['pass']=False;benchmark['data_failure']='Incorrect n series'
                        if any(row['status']!='SAT' or row['blind_candidates']!=2**row['n'] for row in b['rows']):
                            benchmark['pass']=False;benchmark['data_failure']='Baseline count/certificate mismatch'
                    except (ValueError,KeyError,TypeError,OSError) as e:
                        benchmark['pass']=False;benchmark['data_failure']=str(e)
                distrib=run_command(name+'/distributions',[sys.executable,'high_probability_harness.py'],work,180,report['checks'])
                if distrib['pass']:
                    try:
                        d=json.loads((work/'distribution_results_08.json').read_text(encoding='utf8'))
                        item['distributions']={'master_seed':d.get('master_seed'),'summary':d['summary'],
                                               'limitations':d.get('limitations')}
                        if not d['raw'] or len(d['summary'])<6 or any(row['verifier_failure'] for row in d['raw']):
                            distrib['pass']=False;distrib['data_failure']='Missing samples or verifier failure'
                    except (ValueError,KeyError,TypeError,OSError) as e:
                        distrib['pass']=False;distrib['data_failure']=str(e)
        report['frozen_integrity_after']=verify_frozen()
        if not report['frozen_integrity_after']['pass']:
            report['checks'].append({'label':'frozen_integrity_after','pass':False})
    report['passing_checks']=sum(x['pass'] for x in report['checks'])
    report['total_checks']=len(report['checks'])
    report['all_checks_pass']=all(x['pass'] for x in report['checks']) and report['frozen_integrity_after']['pass']
    candidate_rows=report['evidence']['candidate'].get('benchmark',{}).get('rows',[])
    baseline_rows=report['evidence']['baseline'].get('benchmark',{}).get('rows',[])
    benchmark_comparison=[]
    if candidate_rows and baseline_rows:
        by_n={x['n']:x for x in baseline_rows}
        for c in candidate_rows:
            b=by_n.get(c['n'])
            if not b:continue
            benchmark_comparison.append({'n':c['n'],
                                         'baseline_v08_work_units':b['mstar_08_meter_work'],
                                         'candidate_work_units':c['mstar_08_meter_work'],
                                         'same_meter':True,
                                         'candidate_over_baseline':round(c['mstar_08_meter_work']/b['mstar_08_meter_work'],4)})
    report['evidence']['work_comparison_v08_to_candidate']=benchmark_comparison
    report['scientific_gates']={
        'functional_regression_gate':('PASS' if report['all_checks_pass'] else 'FAIL'),
        'general_purpose_ATP':'NOT ESTABLISHED: additional target-independent calculi and held-out proofs needed',
        'competitive_speedup':'NOT ESTABLISHED: fair strong-solver comparison under equal resource measures needed',
        'exponential_to_linear_restricted':'PREVIOUS v0.8 FAMILY ONLY: exponential exhaustive candidate count versus linear clause/literal primitives; bit-cost and fair comparison not proved',
        'external_third_party_certificate_validation':'NOT RUN',
        'new_mathematical_theorem':'NONE CLAIMED'
    }
    (out/'AUTOPILOT_RESULT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    lines=[f'# M* Automated Development Report',
           '',f"Date (UTC): {report['created_utc']}",
           f"Mode: `{mode}` · Candidate files: {report['candidate_source']['file_count']}",
           '',f"**Engineering status: {'PASS' if report['all_checks_pass'] else 'FAIL'} — {report['passing_checks']}/{report['total_checks']} checks**",
           '', '## Individual checks','', '| Check | Status | Time (s) |','|---|---|---:|']
    for item in report['checks']:
        lines.append(f"| {item['label']} | {'PASS' if item['pass'] else 'FAIL'} | {item.get('wall_seconds',0):.3f} |")
    lines+=['','## Research claim boundaries','',
            '- A local regression PASS does **not** establish general-purpose ATP capability.',
            '- The unit-CNF contrast is against intentionally exhaustive assignment enumeration, **not** a competitive SAT solver.',
            '- The development work meter is not interchangeable with wall-clock time or bit complexity.',
            '- The verifier is separate from search, but has not been audited externally.',
            '- No files have been published or pushed to any account.','',
            '## Next research gates','',
            '1. Implement small-step, work-bounded guide/reserve scheduling with property-based fairness tests.',
            '2. Add first-order unification and resolution with independent proof replay and a proof DAG.',
            '3. Hold out test problems and compare with goal-aware conventional prover baselines.',
            '4. Formalize an infinite problem family and equal-resource complexity metric before claiming a speedup.',
            '5. Integrate maintained external checkers and independently review all experimental claims.','']
    (out/'AUTOPILOT_REPORT.md').write_text('\n'.join(lines),encoding='utf8')
    print(f"AUTOPILOT {'PASS' if report['all_checks_pass'] else 'FAIL'}: {report['passing_checks']}/{report['total_checks']} checks")
    print('Detailed report:',out/'AUTOPILOT_REPORT.md')
    return 0 if report['all_checks_pass'] else 1

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['quick','full'],default='full')
    ap.add_argument('--candidate',type=Path,default=DEFAULT_CANDIDATE)
    ap.add_argument('--output',type=Path,default=ROOT/'results'/'latest')
    args=ap.parse_args()
    try:sys.exit(pipeline(args.candidate,args.mode,args.output))
    except Exception as e:
        print('AUTOPILOT ERROR:',repr(e),file=sys.stderr)
        sys.exit(2)
if __name__=='__main__':main()
