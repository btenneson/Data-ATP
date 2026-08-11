#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,os,re,shlex,statistics,subprocess,sys,tempfile,time
from collections import defaultdict,deque
from pathlib import Path
TIME=30; GRACE=5; MEM_KB=4*1024*1024
HERE=Path(__file__).resolve().parent
EDGE_RE=re.compile(r"fof\(\s*(a\d+)\s*,\s*axiom\s*,\s*\(\s*p\(n(\d+)\)\s*=>\s*p\(n(\d+)\)\s*\)\s*\)\s*\.")
START_RE=re.compile(r"fof\(start,axiom,p\(n(\d+)\)\)\.")
GOAL_RE=re.compile(r"fof\(goal,conjecture,p\(n(\d+)\)\)\.")
SZS_THEOREM=re.compile(r"SZS status\s+(Theorem|Unsatisfiable)",re.I)
SZS_OTHER=re.compile(r"SZS status\s+(CounterSatisfiable|Satisfiable|GaveUp|Unknown|Timeout|ResourceOut|MemoryOut)",re.I)
INF_REC=re.compile(r"\binference\s*\(")
PRO_CMDS={
 'Vampire':lambda p:[os.environ['VAMPIRE_BIN'],'--mode','casc','-t',str(TIME),'-p','tptp',str(p)],
 'E':lambda p:[os.environ['EPROVER_BIN'],'--auto',f'--cpu-limit={TIME}','--proof-object',str(p)],
 'iProver':lambda p:[os.environ['IPROVER_BIN'],'--time_out_real',str(TIME),str(p)],
 'Prover9':lambda p:[os.environ['PROVER9_BIN'],'-tptp','-tptp_out','-t',str(TIME),'-f',str(p)],}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def parse_peak(s):
 m=re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',s);return int(m.group(1))/1024 if m else None

def run_limited(cmd,log,timefile,extra_env=None):
 env=os.environ.copy(); env.update(extra_env or {})
 wrapped=f"ulimit -v {MEM_KB}; exec {shlex.join(cmd)}"; full=['/usr/bin/time','-v','-o',str(timefile),'bash','-lc',wrapped]
 t0=time.perf_counter(); timed=False
 try:
  cp=subprocess.run(full,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=TIME+GRACE,env=env,stdin=subprocess.DEVNULL);rc=cp.returncode;text=cp.stdout
 except subprocess.TimeoutExpired as e:
  timed=True;rc=124;text=e.stdout if isinstance(e.stdout,str) else ''
 wall=time.perf_counter()-t0;Path(log).write_text(text,encoding='utf-8',errors='replace')
 rtxt=Path(timefile).read_text(errors='replace') if Path(timefile).exists() else ''
 return rc,text,wall,parse_peak(rtxt),timed

def independent_path_check(problem,path):
 s=t=None;es=set()
 for line in Path(problem).read_text().splitlines():
  m=START_RE.fullmatch(line.strip())
  if m:s=int(m.group(1));continue
  m=GOAL_RE.fullmatch(line.strip())
  if m:t=int(m.group(1));continue
  m=EDGE_RE.fullmatch(line.strip())
  if m:es.add((int(m.group(2)),int(m.group(3))))
 return bool(path and s is not None and t is not None and path[0]==s and path[-1]==t and all((u,v) in es for u,v in zip(path,path[1:])))

def compact_reference_json(jpath,problem,certpath):
 r=json.loads(Path(jpath).read_text());path=r.pop('path',None);verified=independent_path_check(problem,path) if path else False
 if r.get('status') in {'PROVED','CERTIFIED_MINIMUM'} and not verified:r['status']='AUDIT_FAILURE'
 if path and verified:
  with gzip.open(certpath,'wt',encoding='utf-8') as f:f.write('\n'.join(map(str,path))+'\n')
  r['independent_certificate_verified']=True;r['certificate_gz_sha256']=sha(certpath);r['proof_length']=len(path)-1
 else:r['independent_certificate_verified']=False
 Path(jpath).write_text(json.dumps(r,indent=2),encoding='utf-8');return r

def mk_sandbox(root,oid,all_rows,learning,negated=False):
 td=tempfile.TemporaryDirectory(prefix='ocean_eval_');d=Path(td.name);src=root/'solver_inputs'/('notald' if negated else 'standard')/(oid+'.p');(d/'problem.p').symlink_to(src.resolve());train=d/'training';train.mkdir()
 if learning:
  me=next(x for x in all_rows if x['opaque_id']==oid);smaller=[x for x in all_rows if x['Lstar']<me['Lstar']];idx=[]
  for x in smaller:
   sub=train/x['opaque_id'];sub.mkdir();(sub/'problem.p').symlink_to((root/'solver_inputs'/'standard'/(x['opaque_id']+'.p')).resolve())
   with gzip.open(sub/'certificate.nodes.gz','wt',encoding='utf-8') as f:f.write('\n'.join(map(str,x['certificate_path']))+'\n')
   idx.append({'opaque_id':x['opaque_id'],'problem':'problem.p','certificate':'certificate.nodes.gz'})
  (train/'index.json').write_text(json.dumps(idx,indent=2))
 return td,d,d/'problem.p',train

def run_ref(label,mode,problem,train,outdir):
 outdir.mkdir(parents=True,exist_ok=True);j=outdir/'result.json';log=outdir/'stdout.log';tf=outdir/'resource.txt';cert=outdir/'certificate.nodes.gz';script=Path('benchmarks/ocean_reference/reference_solvers.py')
 cmd=[sys.executable,str(script),'--solver',mode,'--problem',str(problem),'--out',str(j)];rc,text,wall,mem,timed=run_limited(cmd,log,tf,{'OCEAN_TRAINING_BUNDLE':str(train)})
 if timed:return {'solver':label,'status':'BOUNDED_UNKNOWN','wall_s':wall,'peak_memory_mib':mem,'returncode':124,'training_consumed':False}
 if rc!=0 or not j.exists():return {'solver':label,'status':'INFRASTRUCTURE_FAULT','wall_s':wall,'peak_memory_mib':mem,'returncode':rc,'training_consumed':False}
 r=compact_reference_json(j,problem,cert);return {'solver':label,'status':r['status'],'wall_s':wall,'peak_memory_mib':mem,'returncode':rc,'charged_expansions':r.get('expansions'),'proof_length':r.get('proof_length'),'certificate_verified':r.get('independent_certificate_verified',False),'training_consumed':False,'scoring_edge_probes':r.get('scoring_edge_probes')}

def run_control(label,mode,problem,outdir):
 outdir.mkdir(parents=True,exist_ok=True);j=outdir/'result.json';log=outdir/'stdout.log';tf=outdir/'resource.txt';cert=outdir/'certificate.nodes'
 cmd=[sys.executable,str(HERE/'ocean_reference_controls.py'),'--solver',mode,'--problem',str(problem),'--out',str(j),'--cert',str(cert)];rc,text,wall,mem,timed=run_limited(cmd,log,tf)
 if timed:return {'solver':label,'status':'BOUNDED_UNKNOWN','wall_s':wall,'peak_memory_mib':mem,'returncode':124}
 if rc!=0 or not j.exists():return {'solver':label,'status':'INFRASTRUCTURE_FAULT','wall_s':wall,'peak_memory_mib':mem,'returncode':rc}
 r=json.loads(j.read_text());return {'solver':label,**{k:r.get(k) for k in ['status','expansions','proof_length','certificate_verified','P_status','P_expansions','R_status','R_expansions','I_status','I_expansions','shared_lemmas_produced','cross_role_reuse']},'charged_expansions':r.get('expansions'),'wall_s':wall,'peak_memory_mib':mem,'returncode':rc,'training_consumed':False}

def run_pro(name,problem,outdir):
 outdir.mkdir(parents=True,exist_ok=True);log=outdir/'proof.out';tf=outdir/'resource.txt';audit=outdir/'audit.json';key={'Vampire':'VAMPIRE_BIN','E':'EPROVER_BIN','iProver':'IPROVER_BIN','Prover9':'PROVER9_BIN'}[name]
 if not os.environ.get(key):return {'solver':name,'status':'INFRASTRUCTURE_FAULT','reason':'binary unavailable','wall_s':0.0,'peak_memory_mib':None}
 cmd=PRO_CMDS[name](problem);rc,text,wall,mem,timed=run_limited(cmd,log,tf)
 if timed:return {'solver':name,'status':'BOUNDED_UNKNOWN','wall_s':wall,'peak_memory_mib':mem,'returncode':124,'certificate_verified':False,'native_inference_records':len(INF_REC.findall(text))}
 if SZS_THEOREM.search(text):
  subprocess.run([sys.executable,str(HERE/'verify_professional_ocean_proof.py'),'--problem',str(problem),'--output',str(log),'--out',str(audit)],capture_output=True,text=True);ar=json.loads(audit.read_text()) if audit.exists() else {'certificate_verified':False};st='PROVED' if ar.get('certificate_verified') else 'AUDIT_FAILURE'
  return {'solver':name,'status':st,'wall_s':wall,'peak_memory_mib':mem,'returncode':rc,'certificate_verified':bool(ar.get('certificate_verified')),'proof_length':ar.get('proof_length'),'native_inference_records':len(INF_REC.findall(text)),'audit_reason':ar.get('reason')}
 m=SZS_OTHER.search(text)
 if m:return {'solver':name,'status':'BOUNDED_UNKNOWN' if m.group(1).lower() in {'gaveup','unknown','timeout','resourceout','memoryout'} else 'WRONG_STATUS','szs_status':m.group(1),'wall_s':wall,'peak_memory_mib':mem,'returncode':rc,'certificate_verified':False}
 return {'solver':name,'status':'INFRASTRUCTURE_FAULT' if rc else 'UNKNOWN_OUTPUT','wall_s':wall,'peak_memory_mib':mem,'returncode':rc,'certificate_verified':False}

def write_rows(path,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with open(path,'w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=json.loads((root/'evaluator_only'/'answer_key.json').read_text());results=[];rows=sorted(rows,key=lambda x:(x['Lstar'],x['seed_index']))
 for idx,meta in enumerate(rows,1):
  oid=meta['opaque_id'];L=meta['Lstar'];print(f"EVAL {idx}/{len(rows)} depth={L} id={oid}",flush=True);per=out/'per_instance'/oid
  td,d,p,train=mk_sandbox(root,oid,rows,True,False)
  try:
   rr=[run_control('Depths-F','depths-f',p,per/'Depths-F'),run_ref('Data-ATP','data-atp',p,train,per/'Data-ATP'),run_ref('Data 2.0.1','data2-fast',p,train,per/'Data_2.0.1')]
   for name in ['Vampire','E','iProver','Prover9']:
    rr.append(run_pro(name,p,per/name));plog=per/name/'proof.out'
    if plog.exists():
     with open(plog,'rb') as src,gzip.open(str(plog)+'.gz','wb',compresslevel=6) as dst:
      while True:
       b=src.read(1024*1024)
       if not b:break
       dst.write(b)
     plog.unlink()
  finally:td.cleanup()
  td,d,p,train=mk_sandbox(root,oid,rows,True,True)
  try:rr.append(run_control('NOTALD','notald',p,per/'NOTALD'))
  finally:td.cleanup()
  for r in rr:
   expected='REFUTED' if r['solver']=='NOTALD' else 'PROVED';r.update({'opaque_id':oid,'Lstar':L,'seed_index_evaluator_only':meta['seed_index'],'expected_status_evaluator_only':expected,'correct_certified_settlement':bool(r.get('status')==expected and r.get('certificate_verified',False))})
   if r.get('proof_length') is not None:r['proof_over_Lstar']=r['proof_length']/L
   results.append(r);print(' ',r['solver'],r['status'],f"{r.get('wall_s',0):.3f}s",'cert='+str(r.get('certificate_verified')),flush=True)
  write_rows(out/'rows.csv',results);(out/'rows.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 summary=[]
 for L in sorted({r['Lstar'] for r in results}):
  for system in ['Depths-F','NOTALD','Data-ATP','Data 2.0.1','Vampire','E','iProver','Prover9']:
   x=[r for r in results if r['Lstar']==L and r['solver']==system];solved=[r for r in x if r['correct_certified_settlement']]
   summary.append({'Lstar':L,'solver':system,'certified_correct':len(solved),'n':len(x),'rate':len(solved)/len(x) if x else None,'bounded_unknown':sum(r['status']=='BOUNDED_UNKNOWN' for r in x),'audit_failures':sum(r['status']=='AUDIT_FAILURE' for r in x),'infra_faults':sum(r['status']=='INFRASTRUCTURE_FAULT' for r in x),'median_wall_s_solved':statistics.median([r['wall_s'] for r in solved]) if solved else None,'median_proof_length_solved':statistics.median([r['proof_length'] for r in solved if r.get('proof_length') is not None]) if any(r.get('proof_length') is not None for r in solved) else None})
 (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print('CAMPAIGN_COMPLETE',flush=True)
if __name__=='__main__':main()
