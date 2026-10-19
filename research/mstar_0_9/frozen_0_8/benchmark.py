"""Predeclared unit-CNF diagnostic, NOT a state-of-art performance comparison.

The clause family is x1 & ... & xn. A purposefully simple false-first
exhaustive assignment baseline visits all 2**n candidates before 1...1.
Both baselines process the identical CNF and accept only checked models.
A competent SAT solver with unit propagation is O(n) too.
"""
import json,time
from pathlib import Path
from core.search import solve
from core.verify import verify

def instance(n):
    return {'system':'sat-cnf','variables':n,'clauses':[[i] for i in range(1,n+1)]}

def exhaustive_false_first(problem):
    n=problem['variables'];count=0;literal_scans=0
    for mask in range(1<<n):
        count+=1
        a=[bool(mask&(1<<(n-i-1))) for i in range(n)]
        good=True
        for clause in problem['clauses']:
            for lit in clause:
                literal_scans+=1
                if a[abs(lit)-1] == (lit>0):break
            else:good=False;break
        if good:
            cert={'kind':'sat-model','assignment':a}
            verify(problem,cert)
            return {'attempts':count,'literal_scans':literal_scans,'certificate_bytes':len(json.dumps(cert))}
    return {'attempts':count,'literal_scans':literal_scans,'certificate_bytes':0}

def run(sizes=(4,6,8,10,12,14,16)):
    rows=[]
    for n in sizes:
        p=instance(n)
        t=time.perf_counter();baseline=exhaustive_false_first(p)
        t_baseline=time.perf_counter()-t
        got=solve(p,max_work=10000000,max_ticks=40)
        assert got['status']=='SAT' and got['receipt']['assignment']==[True]*n
        v=verify(p,got['receipt'])
        rows.append({'n':n,'encoded_input_bytes':len(json.dumps(p,sort_keys=True)),
                     'blind_candidates':baseline['attempts'],
                     'blind_literal_scans':baseline['literal_scans'],
                     'blind_wall_seconds':round(t_baseline,6),
                     'mstar_08_meter_work':got['total_measured_work_units'],
                     'mstar_wall_seconds':got['wall_seconds'],
                     'mstar_certificate_verify_literal_scans':v,
                     'mstar_proof_bytes':got['proof_bytes'],
                     'status':got['status']})
    return {'family':'unit-CNF all positive literals; false-first assignment baseline',
            'baseline':'brute-force truth assignments, lexicographic false before true',
            'warning':'Both M* and standard unit propagation solve this family in linear unit-cost clause/literal operations; no relative advantage against competent SAT solvers. JSON byte costs not linear in n due to index lengths.',
            'rows':rows}

if __name__=='__main__':
    r=run()
    out=Path('benchmark_results_08.json')
    out.write_text(json.dumps(r,indent=2)+'\n')
    print('n | exhaustive candidates | M* metered work | checked')
    for row in r['rows']: print(row['n'],row['blind_candidates'],row['mstar_08_meter_work'],row['status'])
