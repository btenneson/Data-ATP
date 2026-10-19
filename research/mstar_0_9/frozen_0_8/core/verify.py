"""Independent-of-search certificate verifier for the M* 0.8 bridge.

No import from core.search. The verifier cannot trust an unverified 'UNSAT'
assertion, a labelled hypothesis, a proof trace, or a proof-system switch.
"""
import json

class InvalidCertificate(ValueError):
    pass

def check_horn(problem, cert):
    if cert.get('kind') != 'horn' or not isinstance(cert.get('steps'), list):
        raise InvalidCertificate('bad Horn certificate schema')
    known = set()
    facts = problem['facts']; rules = problem['rules']
    operations = 0
    for step in cert['steps']:
        if set(step) == {'fact'} and type(step['fact']) is int:
            i = step['fact']
            if not 0 <= i < len(facts): raise InvalidCertificate('unknown fact')
            known.add(facts[i]); operations += 1
        elif set(step) == {'rule'} and type(step['rule']) is int:
            i = step['rule']
            if not 0 <= i < len(rules): raise InvalidCertificate('unknown rule')
            rule = rules[i]
            if not all(x in known for x in rule['if']):
                raise InvalidCertificate('uncertified Horn premise')
            known.add(rule['then']); operations += 1 + len(rule['if'])
        else:
            raise InvalidCertificate('unknown Horn step')
    if problem['goal'] not in known:
        raise InvalidCertificate('no certificate for target')
    return operations

def norm_clause(clause):
    if not isinstance(clause, list) or not all(type(a) is int and a != 0 for a in clause):
        raise InvalidCertificate('ill-typed input clause')
    return frozenset(clause)

def check_sat(problem, cert):
    clauses = [norm_clause(c) for c in problem['clauses']]
    n = problem['variables']
    if type(n) is not int or n < 0 or any(abs(a) > n for c in clauses for a in c):
        raise InvalidCertificate('invalid variable index')
    kind = cert.get('kind')
    operations = 0
    if kind == 'sat-model':
        assignment = cert.get('assignment')
        if not isinstance(assignment, list) or len(assignment) != n or not all(type(b) is bool for b in assignment):
            raise InvalidCertificate('malformed model')
        for clause in clauses:
            operations += len(clause)
            if not any(assignment[abs(a)-1] == (a > 0) for a in clause):
                raise InvalidCertificate('model falsifies a clause')
        return operations
    if kind != 'resolution-unsat':
        raise InvalidCertificate('SAT requires checked model or resolution refutation')
    steps = cert.get('steps')
    if not isinstance(steps, list): raise InvalidCertificate('malformed resolution steps')
    known = list(clauses)
    for step in steps:
        if set(step) != {'left','right','pivot','resolvent'}: raise InvalidCertificate('bad resolution step')
        l,r,p = step['left'],step['right'],step['pivot']
        if not (type(l) is type(r) is type(p) is int and p > 0 and 0 <= l < len(known) and 0 <= r < len(known)):
            raise InvalidCertificate('invalid parent or pivot')
        a,b = known[l],known[r]
        if p in a and -p in b:
            result = (a-{p}) | (b-{-p})
        elif -p in a and p in b:
            result = (a-{-p}) | (b-{p})
        else:
            raise InvalidCertificate('parents do not resolve on pivot')
        wanted = step['resolvent']
        if not isinstance(wanted,list) or any(type(k) is not int or k==0 for k in wanted):
            raise InvalidCertificate('invalid resolvent syntax')
        if frozenset(wanted) != result or len(set(wanted)) != len(wanted):
            raise InvalidCertificate('incorrect resolvent')
        known.append(result); operations += len(a)+len(b)+len(result)+1
    if frozenset() not in known:
        raise InvalidCertificate('no derived empty clause')
    return operations

def check_metamath(problem, cert, db):
    if cert.get('kind') != 'metamath-rpn':
        raise InvalidCertificate('bad Metamath certificate kind')
    labels = cert.get('labels')
    if not isinstance(labels,list) or not all(isinstance(x,str) for x in labels):
        raise InvalidCertificate('invalid RPN labels')
    from legacy_mm.mm_core import MMError
    try:
        db.verify(problem['goal'].split(), labels)
    except MMError as exc:
        raise InvalidCertificate(str(exc)) from exc
    return len(labels)

def verify(problem, certificate, db=None):
    if not isinstance(certificate, dict): raise InvalidCertificate('certificate must be an object')
    ptype = problem.get('system')
    if ptype == 'horn': return check_horn(problem,certificate)
    if ptype == 'sat-cnf': return check_sat(problem,certificate)
    if ptype == 'metamath':
        if db is None: raise InvalidCertificate('frozen database required')
        return check_metamath(problem,certificate,db)
    raise InvalidCertificate('unknown proof system')

def verify_bytes(problem, candidate_bytes, db=None):
    try:
        cert=json.loads(candidate_bytes.decode('utf8'))
        return cert, verify(problem,cert,db)
    except (UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        raise InvalidCertificate(str(exc)) from exc
