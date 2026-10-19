"""Finite distribution-relative test harness inspired by the September 2026
Preorders and Fair Settlement Geometry protocol. No asymptotic theorem claimed.
"""
import hashlib,json,math,random,statistics,time
from core.search import solve
from core.verify import verify,InvalidCertificate

def seed(master,family,n,j,role):
    return int.from_bytes(hashlib.sha256(f'{master}/{family}/{n}/{j}/{role}'.encode()).digest()[:8],'big')

def sample(n,instance_seed,family):
    rng=random.Random(instance_seed)
    if family=='random_3sat':
        clauses=[]
        for _ in range(round(4.2*n)):
            variables=rng.sample(range(1,n+1),3)
            clauses.append([v*(1 if rng.randrange(2) else -1) for v in variables])
        return {'system':'sat-cnf','variables':n,'clauses':clauses}
    if family=='planted_3sat':
        planted=[bool(rng.getrandbits(1)) for _ in range(n)]
        clauses=[]
        for _ in range(round(4.2*n)):
            variables=rng.sample(range(1,n+1),3)
            while True:
                clause=[v*(1 if rng.randrange(2) else -1) for v in variables]
                if any(planted[abs(l)-1]==(l>0) for l in clause):break
            clauses.append(clause)
        return {'system':'sat-cnf','variables':n,'clauses':clauses}
    raise ValueError('unknown family')

def wilson(k,N,z=1.95996398454):
    if N==0:return [0,1]
    p=k/N;d=1+z*z/N
    center=(p+z*z/(2*N))/d
    margin=(z/d)*math.sqrt(p*(1-p)/N+z*z/(4*N*N))
    return [round(max(0,center-margin),4),round(min(1,center+margin),4)]

def execute(families=('random_3sat','planted_3sat'),ns=(4,6,8),trials=12,master_seed=20261018,max_work=150000):
    raw=[];summary=[]
    for family in families:
        for n in ns:
            subset=[]
            for j in range(trials):
                s=seed(master_seed,family,n,j,'instance')
                ss=seed(master_seed,family,n,j,'solver')
                problem=sample(n,s,family)
                started=time.perf_counter()
                result=solve(problem,max_work=max_work,max_ticks=20)
                elapsed=round(time.perf_counter()-started,6)
                verify_failure=False
                if result['status']!='UNKNOWN':
                    try:verify(problem,result['receipt'])
                    except (InvalidCertificate,ValueError,TypeError,KeyError):verify_failure=True
                record={'family':family,'n_variables':n,'sample_index':j,'instance_seed':s,'solver_seed_logged_not_used':ss,
                        'input_json_bytes':len(json.dumps(problem,sort_keys=True,separators=(',',':'))),
                        'status':result['status'],'verified':result['status']!='UNKNOWN' and not verify_failure,
                        'verifier_failure':verify_failure,'work':result['total_measured_work_units'],
                        'wall_seconds':elapsed,'certificate_bytes':result['proof_bytes'],
                        'problem_sha256':result['problem_digest']}
                subset.append(record);raw.append(record)
            k=sum(x['verified'] for x in subset)
            summary.append({'family':family,'n':n,'samples':trials,'certified':k,
                            'unknown':sum(x['status']=='UNKNOWN' for x in subset),
                            'verifier_failures':sum(x['verifier_failure'] for x in subset),
                            'settled_fraction':k/trials,'wilson95_ci':wilson(k,trials),
                            'median_meter_work':statistics.median(x['work'] for x in subset),
                            'max_meter_work':max(x['work'] for x in subset)})
    return {'format':'MSTAR-0.8-HP-PROTOCOL-FINITE','master_seed':master_seed,
            'budget_units':max_work,'families':list(families),
            'limitations':'Finite samples cannot establish limit probability 1 or polynomial-time high-probability settlement. SAT generator is not representative of all distributions.',
            'summary':summary,'raw':raw}

if __name__=='__main__':
    out=execute()
    with open('distribution_results_08.json','w') as f:json.dump(out,f,indent=2)
    for row in out['summary']:
        print(row['family'],row['n'],row['certified'],'/',row['samples'],'95% CI',row['wilson95_ci'])
