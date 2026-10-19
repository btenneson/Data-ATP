import unittest
from pathlib import Path
from core.search import solve,FairBinaryReserve
from core.verify import verify,verify_bytes,InvalidCertificate

class TestMstar08(unittest.TestCase):
    def test_horn_multistep(self):
        p={'system':'horn','facts':['a'],'rules':[{'if':['a'],'then':'b'},{'if':['b'],'then':'c'}],'goal':'c'}
        r=solve(p)
        self.assertEqual(r['status'],'PROVED')
        self.assertGreater(verify(p,r['receipt']),0)
        self.assertEqual(r['problem_digest'],solve(p)['problem_digest'])
    def test_horn_unreachable_unknown(self):
        p={'system':'horn','facts':['a'],'rules':[{'if':['b'],'then':'c'}],'goal':'c'}
        self.assertEqual(solve(p,max_ticks=8)['status'],'UNKNOWN')
    def test_horn_reject_fake(self):
        p={'system':'horn','facts':['a'],'rules':[{'if':['b'],'then':'c'}],'goal':'c'}
        with self.assertRaises(InvalidCertificate):
            verify(p,{'kind':'horn','steps':[{'rule':0}]})
    def test_sat_model(self):
        p={'system':'sat-cnf','variables':3,'clauses':[[1,2],[-1,3],[-2,3]]}
        r=solve(p)
        self.assertEqual(r['status'],'SAT')
        self.assertGreater(verify(p,r['receipt']),0)
    def test_sat_unsat_unit_pair(self):
        p={'system':'sat-cnf','variables':1,'clauses':[[1],[-1]]}
        r=solve(p)
        self.assertEqual(r['status'],'UNSAT',r)
        self.assertEqual(r['receipt']['resolvent'] if 'resolvent' in r['receipt'] else r['receipt']['steps'][-1]['resolvent'],[])
        self.assertGreater(verify(p,r['receipt']),0)
    def test_sat_unsat_four_clauses(self):
        p={'system':'sat-cnf','variables':2,'clauses':[[1,2],[1,-2],[-1,2],[-1,-2]]}
        r=solve(p,max_work=400000)
        self.assertEqual(r['status'],'UNSAT',r)
        self.assertGreater(verify(p,r['receipt']),0)
    def test_sat_reject_fake_unsat(self):
        p={'system':'sat-cnf','variables':1,'clauses':[[1]]}
        with self.assertRaises(InvalidCertificate): verify(p,{'kind':'resolution-unsat','steps':[]})
    def test_sat_reject_bad_model(self):
        p={'system':'sat-cnf','variables':1,'clauses':[[1]]}
        with self.assertRaises(InvalidCertificate):verify(p,{'kind':'sat-model','assignment':[False]})
    def test_sat_corrupted_resolvent(self):
        p={'system':'sat-cnf','variables':1,'clauses':[[1],[-1]]}
        with self.assertRaises(InvalidCertificate):verify(p,{'kind':'resolution-unsat','steps':[{'left':0,'right':1,'pivot':1,'resolvent':[1]}]})
    def test_metamath_fixture(self):
        from legacy_mm.mm_core import Database
        db=Database.load(Path(__file__).resolve().parents[1]/'legacy_mm'/'demo0_base.mm')
        p={'system':'metamath','goal':'|- ( t + 0 ) = t'}
        r=solve(p,db=db)
        self.assertEqual(r['status'],'PROVED',r)
        self.assertGreater(verify(p,r['receipt'],db=db),0)
    def test_metamath_bad_goal_rejected(self):
        from legacy_mm.mm_core import Database
        db=Database.load(Path(__file__).resolve().parents[1]/'legacy_mm'/'demo0_base.mm')
        with self.assertRaises(InvalidCertificate):
            verify({'system':'metamath','goal':'|- ( t + 0 ) = r'}, {'kind':'metamath-rpn','labels':['tt','a2']},db)
    def test_fair_reserve_uses_binary_alphabet(self):
        reserve=FairBinaryReserve()
        self.assertEqual([next(reserve) for _ in range(4)],[b'',b'\x00',b'\x01',b'\x02'])
    def test_reserve_gets_ticks_on_unreachable_goal(self):
        p={'system':'horn','facts':[],'rules':[],'goal':'z'}
        r=solve(p,max_ticks=8,period=2)
        self.assertEqual(r['reserve_attempts'],8)
    def test_budget_unknown_not_false(self):
        p={'system':'sat-cnf','variables':2,'clauses':[[1,2],[1,-2],[-1,2],[-1,-2]]}
        r=solve(p,max_work=1,max_ticks=3)
        self.assertEqual(r['status'],'UNKNOWN')
    def test_malicious_untrusted_payload(self):
        p={'system':'horn','facts':['a'],'rules':[],'goal':'a'}
        with self.assertRaises(InvalidCertificate):verify_bytes(p,b'__import__("os").system("echo BAD")')

if __name__=='__main__':unittest.main()
