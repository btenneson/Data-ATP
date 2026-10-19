"""Untrusted search-side M* 0.8 bridge: Horn, SAT-CNF, finite Metamath.

No search result becomes a theorem unless core.verify accepts its certificate.
This is a multi-calculus prototype, not a generally competitive ATP.
"""
from __future__ import annotations
from collections import defaultdict,deque
from dataclasses import dataclass
from pathlib import Path
import hashlib,itertools,json,time
from .verify import verify_bytes, InvalidCertificate

class WorkLimit(Exception): pass

@dataclass
class Meter:
    limit:int
    operations:int=0
    def add(self,n=1):
        self.operations+=n
        if self.operations>self.limit: raise WorkLimit('work budget exhausted')

class FairBinaryReserve:
    """All finite byte strings in length-lexicographic order, independent of goal.
    The empty string is first. Every finite UTF8 JSON certificate eventually appears.
    This does not promise affordable time to reach it.
    """
    def __init__(self): self.length=0;self.value=0
    def __next__(self):
        if self.length==0:
            self.length=1
            return b''
        s=self.value.to_bytes(self.length,'big')
        self.value+=1
        if self.value == (256**self.length):
            self.length+=1;self.value=0
        return s

def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(',',':')).encode('utf8')

def horn_guide(problem,m):
    facts=problem['facts'];rules=problem['rules'];goal=problem['goal']
    steps=[];known=set();queue=deque(); waiting=defaultdict(list)
    missing=[]
    m.add(len(canonical(problem)))
    for i,r in enumerate(rules):
        ants=list(dict.fromkeys(r['if']))
        missing.append(len(ants));m.add(len(ants)+1)
        for a in ants: waiting[a].append(i)
    def admit(x,step):
        if x not in known:
            known.add(x);steps.append(step);queue.append(x);m.add()
    for i,x in enumerate(facts): admit(x,{'fact':i})
    for i,r in enumerate(rules):
        if missing[i]==0:admit(r['then'],{'rule':i})
    if goal in known:return {'kind':'horn','steps':steps}
    while queue:
        x=queue.popleft();m.add()
        for i in waiting[x]:
            missing[i]-=1;m.add()
            if missing[i]==0:admit(rules[i]['then'],{'rule':i})
        if goal in known:return {'kind':'horn','steps':steps}
    return None

def sat_guide(problem,m):
    clauses=problem['clauses'];n=problem['variables']
    if type(n) is not int or n<0: return None
    m.add(len(canonical(problem)))
    if not all(isinstance(cl,list) and all(type(lit) is int and lit!=0 and abs(lit)<=n for lit in cl) for cl in clauses):return None
    if any(not clause for clause in clauses):
        return {'kind':'resolution-unsat','steps':[]}
    def dpll(assign):
        while True:
            forced={};all_sat=True
            for clause in clauses:
                m.add()
                sat=False;unassigned=[]
                for lit in clause:
                    m.add()
                    v=abs(lit)
                    if v in assign:
                        if assign[v] == (lit>0):sat=True;break
                    else:unassigned.append(lit)
                if sat:continue
                all_sat=False
                if not unassigned:return None
                if len(unassigned)==1:
                    lit=unassigned[0];v=abs(lit);b=(lit>0)
                    if v in forced and forced[v]!=b:return None
                    forced[v]=b
            if all_sat:return assign
            if not forced:break
            for v,b in forced.items():
                m.add()
                if v in assign and assign[v]!=b:return None
                assign[v]=b
        choices=[v for v in range(1,n+1) if v not in assign]
        m.add(n)
        if not choices:return None
        v=choices[0]
        for b in (False,True):
            m.add()
            result=dpll({**assign,v:b})
            if result is not None:return result
        return None
    model=dpll({})
    if model is not None:
        return {'kind':'sat-model','assignment':[model.get(i,False) for i in range(1,n+1)]}
    # A DPLL failure is not a proof object. Produce independently checked
    # resolution if the budget permits; otherwise return UNKNOWN.
    known=[frozenset(c) for c in clauses]
    indexed={c:i for i,c in enumerate(known)}
    steps=[]
    i=0
    while i<len(known):
        a=known[i]
        for j in range(i):
            b=known[j]
            for v in sorted(set(abs(x) for x in a if -x in b)):
                m.add(len(a)+len(b)+1)
                c=frozenset((a-{v})|(b-{-v})) if v in a else frozenset((a-{-v})|(b-{v}))
                if c in indexed or any(x in c and -x in c for x in c):continue
                indexed[c]=len(known);known.append(c)
                steps.append({'left':i,'right':j,'pivot':v,'resolvent':sorted(c)})
                m.add(len(c)+1)
                if not c:return {'kind':'resolution-unsat','steps':steps}
        i+=1
    return None

def mm_guide(problem,m,db):
    """Legacy bounded axiom-instance adapter. It is intentionally incomplete.
    Searches all suitable axiom schemata, never imports a stored target proof.
    """
    from legacy_mm.mm_core import MMError
    target=tuple(problem['goal'].split());m.add(len(canonical(problem)))
    if target[0] not in db.constants:return None
    for label in db.order:
        s=db.statements[label];m.add()
        if s.kind!='$a' or s.expr[0]!=target[0] or any(db.statements[h].kind=='$e' for h in s.hyps):continue
        # bounded all single-token substitutions from target; not general MM unification
        floating=[db.statements[h] for h in s.hyps]
        symbols=[(v,) for v in dict.fromkeys(target[1:]) if v in db.variables]
        if len(floating)>3 or not symbols:continue
        for vals in itertools.product(symbols,repeat=len(floating)):
            m.add(len(s.expr)+len(floating))
            sub=dict(zip((h.expr[1] for h in floating),vals))
            got=tuple(t for x in s.expr for t in (sub[x] if x in sub else (x,)))
            if got!=target:continue
            code=[]
            for h in floating:
                found=next((fl for fl in db.active_f if db.statements[fl].expr==(h.expr[0],*sub[h.expr[1]])),None)
                if found is None:break
                code.append(found)
            else:
                code.append(label)
                return {'kind':'metamath-rpn','labels':code}
    return None

def solve(problem,*,max_work=100000,max_ticks=300,period=2,db=None):
    """End-to-end tracked prototype run. Errors produce UNKNOWN, not a false proof.

    All search and verification are bounded by max_work for development tests.
    Fairness is conditional on an unbounded tick/work budget.
    """
    started=time.perf_counter(); m=Meter(max_work)
    digest=hashlib.sha256(canonical(problem)).hexdigest()
    reserve=FairBinaryReserve()
    guide=None;guide_error=None;result=None;source=None;ticks=0;reserves=0
    if type(period) is not int or period<2:raise ValueError('period >=2 required')
    try:
        if problem['system']=='horn': guide=horn_guide(problem,m)
        elif problem['system']=='sat-cnf':guide=sat_guide(problem,m)
        elif problem['system']=='metamath' and db is not None:guide=mm_guide(problem,m,db)
        else:guide_error='unsupported system or absent frozen DB'
    except WorkLimit:guide_error='guide exceeded work budget'
    except (KeyError,ValueError,TypeError) as e:guide_error='invalid problem: '+str(e)
    for tick in range(1,max_ticks+1):
        ticks=tick
        if tick%period==0 or guide is None or tick>1:
            c=next(reserve);source='reserve';reserves+=1
        else:
            c=canonical(guide);source='guide'
        try:
            m.add(len(c)+1)
            candidate,verify_work=verify_bytes(problem,c,db)
            m.add(verify_work)
            result=candidate
            break
        except InvalidCertificate:
            pass
        except WorkLimit:
            guide_error='total work budget exhausted'
            break
    out={'format':'MSTAR-0.8-DEV','problem_digest':digest,'system':problem.get('system'),
         'status':'PROVED' if result is not None and problem['system']!='sat-cnf' else
                  ('SAT' if result is not None and result['kind']=='sat-model' else
                   'UNSAT' if result is not None and result['kind']=='resolution-unsat' else 'UNKNOWN'),
         'receipt':result,'tick_attempts':ticks,'reserve_attempts':reserves,
         'total_measured_work_units':m.operations,'work_budget':max_work,
         'guide_error':guide_error,'wall_seconds':round(time.perf_counter()-started,6),
         'proof_bytes':len(canonical(result)) if result else 0,
         'preserved_v07':True,'database_digest':db.digest() if db is not None else None}
    return out
