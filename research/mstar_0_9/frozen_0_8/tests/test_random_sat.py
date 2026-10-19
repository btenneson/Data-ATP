"""Deterministic differential cross-check against exhaustive SAT truth tables.
Small n ONLY: this is a soundness/development check, not complexity research.
"""
import unittest,random,itertools
from core.search import solve
from core.verify import verify

class DifferentialSAT(unittest.TestCase):
    def test_320_deterministic_small_cnf(self):
        rng=random.Random(53)
        checked=0
        for n in range(1,5):
            for _ in range(80):
                clauses=[[rng.choice((-1,1))*rng.randint(1,n)
                          for __ in range(rng.randint(1,3))]
                         for _ in range(rng.randint(1,7))]
                problem={'system':'sat-cnf','variables':n,'clauses':clauses}
                satisfiable=any(all(any(a[abs(lit)-1]==(lit>0) for lit in c)
                                    for c in clauses)
                                for a in itertools.product((False,True),repeat=n))
                result=solve(problem,max_work=1_500_000,max_ticks=2)
                self.assertNotEqual(result['status'],'UNKNOWN')
                verify(problem,result['receipt'])
                self.assertEqual(result['status']=='SAT',satisfiable)
                checked+=1
        self.assertEqual(checked,320)

class BoundarySAT(unittest.TestCase):
    def test_empty_input_clause_is_certified_unsat(self):
        p={'system':'sat-cnf','variables':1,'clauses':[[]]}
        r=solve(p)
        self.assertEqual(r['status'],'UNSAT')
        self.assertEqual(verify(p,r['receipt']),0)
    def test_empty_cnf_is_certified_sat(self):
        p={'system':'sat-cnf','variables':0,'clauses':[]}
        r=solve(p)
        self.assertEqual(r['status'],'SAT')
        self.assertEqual(verify(p,r['receipt']),0)

if __name__=='__main__':unittest.main()
