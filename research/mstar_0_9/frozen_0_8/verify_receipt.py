"""Standalone CLI: independently replay a saved M*0.8 receipt.

Does not import core.search. Uses frozen problem file and standalone checker.
"""
import argparse,hashlib,json
from pathlib import Path
from core.verify import verify, InvalidCertificate

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('problem',type=Path)
    ap.add_argument('receipt',type=Path)
    ap.add_argument('--database',type=Path,default=None)
    a=ap.parse_args()
    p=json.loads(a.problem.read_text());r=json.loads(a.receipt.read_text())
    db=None
    if p.get('system')=='metamath':
        if a.database is None: raise SystemExit('Metamath requires --database')
        from legacy_mm.mm_core import Database
        db=Database.load(a.database)
    digest=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    if digest != r['problem_digest']: raise SystemExit('REJECT: frozen problem digest mismatch')
    if db is not None and db.digest()!=r.get('database_digest'):
        raise SystemExit('REJECT: database digest mismatch')
    if r['status']=='UNKNOWN':
        if r['receipt'] is not None:raise SystemExit('REJECT: UNKNOWN with submitted receipt')
        print('UNKNOWN (no proof certified)');return
    cert=r['receipt']
    try:operations=verify(p,cert,db)
    except (InvalidCertificate,KeyError,TypeError,ValueError) as exc:
        raise SystemExit('REJECT: '+str(exc)) from exc
    implied=('SAT' if cert['kind']=='sat-model' else 'UNSAT' if cert['kind']=='resolution-unsat' else 'PROVED')
    if r['status']!=implied:raise SystemExit('REJECT: claimed settlement class is inconsistent')
    print('ACCEPT:',implied,'independent replay work:',operations,'problem_sha256:',digest)

if __name__=='__main__':main()
