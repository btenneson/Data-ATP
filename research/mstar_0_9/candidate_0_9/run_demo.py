"""Export three readable, independently replayable M*0.8 examples."""
from pathlib import Path
import json
from core.search import solve
from legacy_mm.mm_core import Database

def dump(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def main():
    root=Path(__file__).parent
    results=root/'examples';results.mkdir(exist_ok=True)
    demo=[
        ('horn',{'system':'horn','facts':['start'],'rules':[{'if':['start'],'then':'middle'},
             {'if':['middle'],'then':'goal'}],'goal':'goal'}),
        ('sat',{'system':'sat-cnf','variables':3,'clauses':[[1,2],[-1,3],[-2,3]]}),
        ('unsat',{'system':'sat-cnf','variables':2,
                  'clauses':[[1,2],[1,-2],[-1,2],[-1,-2]]}),
        ('metamath',{'system':'metamath','goal':'|- ( t + 0 ) = t'})]
    mm=Database.load(root/'legacy_mm'/'demo0_base.mm')
    for name,p in demo:
        r=solve(p,db=mm if name=='metamath' else None)
        dump(results/f'{name}_problem.json',p)
        dump(results/f'{name}_result.json',r)
        print(name,r['status'],r['total_measured_work_units'])

if __name__=='__main__':main()
