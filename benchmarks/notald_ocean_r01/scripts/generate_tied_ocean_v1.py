#!/usr/bin/env python3
"""Generate sealed, linearly-scaled tied Ocean instances for R01.

The graph has a required backbone of exactly L edges. Optional detours reconnect
only from b_i to b_{i+1} using >=2 edges, and dead spurs never reconnect. Thus
no added structure can shorten the backbone. An independent BFS still verifies
L* after sealing; that check, not this construction argument, is authoritative.

The same seed determines local structural choices at every L, so smaller-L
siblings are prefixes in structural *pattern*. Each (seed,L) receives a fresh
affine relabelling and hash-ordered presentation, so literal node IDs do not
carry the relation into held-out instances.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from collections import defaultdict, deque
from pathlib import Path

DEPTHS=[10,25,75,100,250,750,1000,2500,7500,10000,25000,75000,100000,250000,750000]
SEEDS=[1729,7919,104729]

def coin(seed:int, i:int, tag:str, modulus=10000):
    h=hashlib.sha256(f"R01|{seed}|{i}|{tag}".encode()).digest()
    return int.from_bytes(h[:8], 'big') % modulus

def build_edges(L:int, seed:int):
    edges=[(i,i+1) for i in range(L)]
    next_id=L+1
    for i in range(L):
        if coin(seed,i,'detour') < 700:
            k=2 + (coin(seed,i,'detour_len') % 2)
            prev=i
            for _ in range(k-1):
                z=next_id; next_id+=1; edges.append((prev,z)); prev=z
            edges.append((prev,i+1))
        if coin(seed,i,'spur') < 900:
            k=1 + (coin(seed,i,'spur_len') % 3)
            prev=i
            for _ in range(k):
                z=next_id; next_id+=1; edges.append((prev,z)); prev=z
    return next_id, edges

def affine_relabel(n:int, seed:int, L:int):
    raw=2 + (coin(seed,L,'affine_a', max(3,n-2)))
    a=raw
    while math.gcd(a,n)!=1:
        a+=1
        if a>=n: a=1
    b=coin(seed,L,'affine_b',n)
    return lambda x:(a*x+b)%n

def bfs(source,target,edges):
    adj=defaultdict(list)
    for u,v in edges: adj[u].append(v)
    q=deque([(source,0)]); seen={source}
    while q:
        u,d=q.popleft()
        if u==target:return d
        for v in adj.get(u,()):
            if v not in seen: seen.add(v); q.append((v,d+1))
    return None

def shortest_path(source,target,edges):
    adj=defaultdict(list)
    for u,v in edges: adj[u].append(v)
    q=deque([source]); parent={source:None}
    while q:
        u=q.popleft()
        if u==target:break
        for v in adj.get(u,()):
            if v not in parent: parent[v]=u; q.append(v)
    if target not in parent:return None
    p=[target]
    while p[-1]!=source:p.append(parent[p[-1]])
    return list(reversed(p))

def opaque_id(seed_index,L):
    return hashlib.sha256(f"NOTALD-OCEAN-R01|{seed_index}|{L}".encode()).hexdigest()[:16]

def write_problem(path,source,target,edges,negated=False):
    def key(uv):
        return hashlib.sha256(f"R01-order|{uv[0]}|{uv[1]}".encode()).digest()
    ordered=sorted(edges,key=key)
    with path.open('w',encoding='utf-8') as f:
        f.write(f"fof(start,axiom,p(n{source})).\n")
        for j,(u,v) in enumerate(ordered):
            f.write(f"fof(a{j:07d},axiom,(p(n{u}) => p(n{v}))).\n")
        goal=f"~p(n{target})" if negated else f"p(n{target})"
        f.write(f"fof(goal,conjecture,{goal}).\n")
    return ordered

def generate_one(root:Path,L:int,seed:int,seed_index:int):
    n,canon=build_edges(L,seed)
    perm=affine_relabel(n,seed,L)
    edges=[(perm(u),perm(v)) for u,v in canon]
    source,target=perm(0),perm(L)
    oid=opaque_id(seed_index,L)
    standard=root/'solver_inputs'/'standard'/f'{oid}.p'
    notald=root/'solver_inputs'/'notald'/f'{oid}.p'
    standard.parent.mkdir(parents=True,exist_ok=True)
    notald.parent.mkdir(parents=True,exist_ok=True)
    ordered=write_problem(standard,source,target,edges,False)
    write_problem(notald,source,target,edges,True)
    d=bfs(source,target,ordered)
    if d!=L: raise RuntimeError(f'BFS audit failed for {oid}: {d} != {L}')
    path=shortest_path(source,target,ordered)
    if path is None or len(path)-1!=L: raise RuntimeError('path audit failed')
    return {
      'opaque_id':oid,'Lstar':L,'seed':seed,'seed_index':seed_index,
      'vertices':n,'edges':len(edges),'source':source,'target':target,
      'bfs_verified_Lstar':d,'certificate_path':path,
      'standard_sha256':hashlib.sha256(standard.read_bytes()).hexdigest(),
      'notald_sha256':hashlib.sha256(notald.read_bytes()).hexdigest()
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True)
    ap.add_argument('--depths',nargs='*',type=int,default=DEPTHS)
    ap.add_argument('--seeds',nargs='*',type=int,default=SEEDS)
    a=ap.parse_args(); root=Path(a.out); root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for si,seed in enumerate(a.seeds,1):
        for L in a.depths:
            r=generate_one(root,L,seed,si); rows.append(r)
            print(f"sealed {r['opaque_id']} vertices={r['vertices']} edges={r['edges']} BFS_OK",flush=True)
    evaluator=root/'evaluator_only'; evaluator.mkdir(exist_ok=True)
    (evaluator/'answer_key.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    public=[{k:v for k,v in r.items() if k not in {'Lstar','seed','seed_index','source','target','bfs_verified_Lstar','certificate_path'}} for r in rows]
    (root/'solver_inputs'/'sealed_manifest.json').write_text(json.dumps(public,indent=2),encoding='utf-8')
    print(f'generated and independently BFS-audited {len(rows)} instances')
if __name__=='__main__':main()
