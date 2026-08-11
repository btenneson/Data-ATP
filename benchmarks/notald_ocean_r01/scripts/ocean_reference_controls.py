#!/usr/bin/env python3
"""Depths-F and NOTALD Ocean implementation-validation references for R01.

These are benchmark-specific controls, not production claims.
"""
from __future__ import annotations
import argparse, hashlib, json, re, time
from collections import defaultdict, deque
from pathlib import Path

START_RE=re.compile(r"fof\(\s*start\s*,\s*axiom\s*,\s*p\(n(\d+)\)\s*\)\s*\.")
GOAL_POS_RE=re.compile(r"fof\(\s*goal\s*,\s*conjecture\s*,\s*p\(n(\d+)\)\s*\)\s*\.")
GOAL_NEG_RE=re.compile(r"fof\(\s*goal\s*,\s*conjecture\s*,\s*~\s*p\(n(\d+)\)\s*\)\s*\.")
EDGE_RE=re.compile(r"fof\(\s*(a\d+)\s*,\s*axiom\s*,\s*\(\s*p\(n(\d+)\)\s*=>\s*p\(n(\d+)\)\s*\)\s*\)\s*\.")

def parse(path:Path):
    s=t=None; neg=None; edges=[]
    for raw in path.read_text(encoding='utf-8').splitlines():
        line=raw.strip()
        if not line: continue
        m=START_RE.fullmatch(line)
        if m: s=int(m.group(1)); continue
        m=GOAL_POS_RE.fullmatch(line)
        if m: t=int(m.group(1)); neg=False; continue
        m=GOAL_NEG_RE.fullmatch(line)
        if m: t=int(m.group(1)); neg=True; continue
        m=EDGE_RE.fullmatch(line)
        if m: edges.append((m.group(1),int(m.group(2)),int(m.group(3))))
    if s is None or t is None or neg is None: raise ValueError('malformed Ocean input')
    adj=defaultdict(list); radj=defaultdict(list)
    for name,u,v in edges: adj[u].append((v,name)); radj[v].append((u,name))
    return s,t,neg,edges,adj,radj

def verify_path(s,t,edge_set,path):
    return bool(path and path[0]==s and path[-1]==t and all((u,v) in edge_set for u,v in zip(path,path[1:])))

def reconstruct_forward(parent,s,t):
    if t not in parent:return None
    p=[t]
    while p[-1]!=s:p.append(parent[p[-1]][0])
    return list(reversed(p))

def depths_f(s,t,edges,radj):
    q=deque([t]); nxt={t:None}; probes=0
    while q:
        v=q.popleft()
        if v==s:break
        for u,name in radj.get(v,()):
            probes+=1
            if u not in nxt: nxt[u]=(v,name); q.append(u)
    if s not in nxt:return {'status':'BOUNDED_UNKNOWN','path':None,'expansions':probes}
    p=[s]
    while p[-1]!=t:p.append(nxt[p[-1]][0])
    return {'status':'PROVED','path':p,'expansions':probes}

def r_bfs(s,t,adj):
    q=deque([s]); parent={s:None}; probes=0
    while q:
        u=q.popleft()
        for v,name in adj.get(u,()):
            probes+=1
            if v not in parent:
                parent[v]=(u,name)
                if v==t:return {'status':'PROVED','path':reconstruct_forward(parent,s,t),'expansions':probes,'lemmas':len(parent)}
                q.append(v)
    return {'status':'BOUNDED_UNKNOWN','path':None,'expansions':probes,'lemmas':len(parent)}

def notald(s,t,neg,edges,adj):
    if not neg: return {'status':'FAULT','error':'NOTALD R01 requires negated conjecture'}
    p_status='BOUNDED_UNKNOWN'; p_work=0
    i_status='BOUNDED_UNKNOWN'; i_work=0
    rr=r_bfs(s,t,adj)
    final='REFUTED' if rr['status']=='PROVED' else 'BOUNDED_UNKNOWN'
    return {
      'status':final,'path':rr.get('path'),'expansions':rr.get('expansions',0),
      'P_status':p_status,'P_expansions':p_work,
      'R_status':rr['status'],'R_expansions':rr.get('expansions',0),
      'I_status':i_status,'I_expansions':i_work,
      'shared_lemmas_produced':rr.get('lemmas',0),'cross_role_reuse':0,
      'double_negation_normalization_charged_ocean_inferences':0
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--solver',choices=['depths-f','notald'],required=True)
    ap.add_argument('--problem',required=True); ap.add_argument('--out',required=True); ap.add_argument('--cert',required=False)
    a=ap.parse_args(); p=Path(a.problem); s,t,neg,edges,adj,radj=parse(p)
    t0=time.perf_counter()
    if a.solver=='depths-f':
        if neg: result={'status':'FAULT','error':'Depths-F expects positive target','path':None,'expansions':0}
        else: result=depths_f(s,t,edges,radj)
        name='Depths-F_Ocean_Control_1.0'; expected='PROVED'
    else:
        result=notald(s,t,neg,edges,adj); name='NOTALD_Ocean_Implementation_Reference_0.1'; expected='REFUTED'
    elapsed=time.perf_counter()-t0
    path=result.get('path'); edge_set={(u,v) for _,u,v in edges}
    verified=verify_path(s,t,edge_set,path) if path else False
    if result['status'] in {'PROVED','REFUTED'} and not verified: result['status']='AUDIT_FAILURE'
    cert_sha=None
    if verified and a.cert:
        cp=Path(a.cert); cp.parent.mkdir(parents=True,exist_ok=True)
        cp.write_text('\n'.join(map(str,path))+'\n',encoding='utf-8')
        cert_sha=hashlib.sha256(cp.read_bytes()).hexdigest()
    result.pop('path', None)
    result.update({'solver':name,'problem':p.name,'wall_s_internal':elapsed,'certificate_verified':verified,'proof_length':len(path)-1 if verified else None,'certificate_sha256':cert_sha,'input_negated':neg,'expected_display_status':expected})
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
