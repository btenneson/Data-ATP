#!/usr/bin/env python3
"""Strict Ocean proof-output audit for professional ATP runs.

For a PROVED claim we look only inside an SZS proof/refutation output block,
collect the named input Ocean edge axioms actually exposed there, and ask
whether those referenced inputs alone contain a source-to-target path.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import defaultdict, deque
from pathlib import Path
START_RE=re.compile(r"fof\(\s*start\s*,\s*axiom\s*,\s*p\(n(\d+)\)\s*\)\s*\.")
GOAL_RE=re.compile(r"fof\(\s*goal\s*,\s*conjecture\s*,\s*p\(n(\d+)\)\s*\)\s*\.")
EDGE_RE=re.compile(r"fof\(\s*(a\d+)\s*,\s*axiom\s*,\s*\(\s*p\(n(\d+)\)\s*=>\s*p\(n(\d+)\)\s*\)\s*\)\s*\.")
SZS_BLOCK_RE=re.compile(r"%\s*SZS output start[^\n]*\n(.*?)%\s*SZS output end",re.I|re.S)
SZS_THEOREM_RE=re.compile(r"SZS status\s+(Theorem|Unsatisfiable)",re.I)
NAME_RE=re.compile(r"\ba\d+\b")

def parse_problem(p):
 s=t=None; emap={}
 for line in Path(p).read_text(encoding='utf-8').splitlines():
  z=line.strip(); m=START_RE.fullmatch(z)
  if m:s=int(m.group(1));continue
  m=GOAL_RE.fullmatch(z)
  if m:t=int(m.group(1));continue
  m=EDGE_RE.fullmatch(z)
  if m:emap[m.group(1)]=(int(m.group(2)),int(m.group(3)))
 if s is None or t is None:raise ValueError('bad positive Ocean problem')
 return s,t,emap

def find_path(s,t,edges):
 adj=defaultdict(list)
 for name,(u,v) in edges.items():adj[u].append((v,name))
 q=deque([s]); par={s:None}
 while q:
  u=q.popleft()
  if u==t:break
  for v,n in adj.get(u,()):
   if v not in par:par[v]=(u,n);q.append(v)
 if t not in par:return None,None
 nodes=[t]; names=[]
 while nodes[-1]!=s:
  u,n=par[nodes[-1]]; names.append(n); nodes.append(u)
 nodes.reverse(); names.reverse(); return nodes,names

def audit(problem,output):
 s,t,emap=parse_problem(problem); text=Path(output).read_text(encoding='utf-8',errors='replace')
 claim=bool(SZS_THEOREM_RE.search(text)); blocks=SZS_BLOCK_RE.findall(text)
 if not claim:return {'claim_theorem':False,'certificate_verified':False,'status':'NO_THEOREM_CLAIM'}
 if not blocks:return {'claim_theorem':True,'certificate_verified':False,'status':'UNVERIFIED_CLAIM','reason':'no SZS proof output block'}
 proof='\n'.join(blocks); used={n:emap[n] for n in set(NAME_RE.findall(proof)) if n in emap}
 nodes,names=find_path(s,t,used)
 if nodes:
  digest=hashlib.sha256(('nodes:'+','.join(map(str,nodes))+'|edges:'+','.join(names)).encode()).hexdigest()
  return {'claim_theorem':True,'certificate_verified':True,'status':'PROVED','proof_length':len(nodes)-1,'referenced_input_edges':len(used),'certificate_path_sha256':digest}
 return {'claim_theorem':True,'certificate_verified':False,'status':'UNVERIFIED_CLAIM','reason':'referenced input axioms in proof block do not independently connect source to target','referenced_input_edges':len(used)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--problem',required=True);ap.add_argument('--output',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 r=audit(a.problem,a.output);Path(a.out).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
if __name__=='__main__':main()
