#!/usr/bin/env python3
"""Small Metamath kernel with both ordinary RPN and compressed proofs.
Scoped hypotheses, mandatory DV, and saved-subproof references are checked.
Search logic is deliberately separate from certificate verification.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re, hashlib

class MMError(ValueError): pass

def require(condition, why):
    if not condition: raise MMError(why)

@dataclass(frozen=True)
class Statement:
    label: str
    kind: str
    expr: tuple[str, ...]
    hyps: tuple[str, ...] = ()
    dv: frozenset[tuple[str,str]] = frozenset()
    proof: tuple[str,...] = ()
    ordinal: int = 0

def decode_compressed(proof, mandatory_hyps):
    """Decode Metamath's standard A..T/U..Y/Z coding into checker operations.

    Returns ("label", name), ("save",), or ("reuse", index).
    No proof is trusted just because it decodes: the verifier checks every step.
    """
    require(proof and proof[0]=='(', 'expected compressed proof opening')
    try: close=proof.index(')')
    except ValueError: raise MMError('unterminated compressed label list')
    explicit=proof[1:close]
    require(all(l not in ('(',')','?') for l in explicit),'bad compressed reference list')
    letters=''.join(proof[close+1:])
    require(bool(letters), 'empty compressed proof')
    references=tuple(mandatory_hyps)+tuple(explicit)
    acc=0
    for char in letters:
        if 'A' <= char <= 'T':
            number=20*acc+(ord(char)-ord('A')+1);acc=0
            if number<=len(references):
                yield ('label',references[number-1])
            else:
                yield ('reuse',number-len(references)-1)
        elif 'U'<=char<='Y':
            acc=5*acc+(ord(char)-ord('U')+1)
        elif char=='Z':
            require(acc==0,'Z within a number')
            yield ('save',)
        else:
            raise MMError(f'illegal compressed character {char!r}')
    require(acc==0, 'trailing incomplete compressed number')

class Database:
    def __init__(self):
        self.statements: dict[str,Statement] = {}
        self.order=[]
        self.constants=set()
        self.variables=set()
        self.active_f=[]
        self.active_e=[]
        self.active_d=set()
        self.stack=[]
        self._ordinal=0

    def _save(self,label,kind,expr,hyps=(),dv=frozenset(),proof=()):
        require(label not in self.statements, f'duplicate statement label {label}')
        self._ordinal+=1
        s=Statement(label,kind,tuple(expr),tuple(hyps),frozenset(dv),tuple(proof),self._ordinal)
        self.statements[label]=s
        self.order.append(label)
        return s

    def _frame(self,expr):
        required={v for v in expr if v in self.variables}
        for e_label in self.active_e:
            required.update(v for v in self.statements[e_label].expr if v in self.variables)
        hypf=[]
        for label in self.active_f:
            if self.statements[label].expr[1] in required:
                hypf.append(label)
        require(len({self.statements[h].expr[1] for h in hypf})==len(required), 'missing active floating hypothesis')
        hyps=hypf+list(self.active_e)
        dv=frozenset((a,b) for a,b in self.active_d if a in required and b in required)
        return tuple(hyps),dv

    @classmethod
    def from_text(cls,src,*,name='<text>'):
        data=re.sub(r'\$\((?:.|\n)*?\$\)', ' ',src)
        toks=data.split(); db=cls(); i=0
        while i<len(toks):
            tok=toks[i]; i+=1
            if tok=='${':
                db.stack.append((len(db.active_f),len(db.active_e),set(db.active_d)))
                continue
            if tok=='$}':
                require(bool(db.stack), 'unbalanced $}')
                nf,ne,dv=db.stack.pop()
                db.active_f=db.active_f[:nf];db.active_e=db.active_e[:ne];db.active_d=dv
                continue
            require(tok!='$[', f'{name}: include syntax unsupported; use a flattened, frozen database')
            if tok in ('$c','$v','$d'):
                try: j=toks.index('$.',i)
                except ValueError: raise MMError('unterminated declaration')
                values=toks[i:j];i=j+1
                require(bool(values),'empty declaration')
                if tok=='$c':
                    require(not db.stack,'$c in scope')
                    for c in values:
                        require(c not in db.variables,'constant is variable')
                        db.constants.add(c)
                elif tok=='$v':
                    for v in values:
                        require(v not in db.constants,'variable is constant')
                        db.variables.add(v)
                else:
                    require(len(values)>=2 and all(v in db.variables for v in values), 'bad $d')
                    for a in range(len(values)):
                        for b in range(a+1,len(values)):
                            db.active_d.add(tuple(sorted((values[a],values[b]))))
                continue
            label=tok
            require(i<len(toks),'statement kind missing')
            kind=toks[i];i+=1
            require(kind in ('$f','$e','$a','$p'),f'{name}: unsupported statement kind {kind}')
            try: j=toks.index('$=' if kind=='$p' else '$.',i)
            except ValueError:raise MMError('unterminated statement')
            expr=toks[i:j];i=j+1
            require(bool(expr) and expr[0] in db.constants,'unknown typecode')
            require(all(t in db.constants or t in db.variables for t in expr),'undeclared expression symbol')
            if kind=='$f':
                require(len(expr)==2 and expr[1] in db.variables,'bad $f')
                db._save(label,kind,expr)
                db.active_f.append(label)
            elif kind=='$e':
                db._save(label,kind,expr)
                db.active_e.append(label)
            else:
                hyps,dv=db._frame(expr)
                if kind=='$p':
                    try: j=toks.index('$.',i)
                    except ValueError: raise MMError('unterminated proof')
                    proof=toks[i:j];i=j+1
                    require(bool(proof), 'empty $p proof')
                    require('?' not in proof,'incomplete proof in database')
                    db._save(label,kind,expr,hyps,dv,proof)
                    # Never import an unchecked prior theorem as an axiom.
                    db.verify(expr,proof,active_dv=db.active_d,
                              legal_before=len(db.order)-1,expected_hyps=tuple(db.active_e),
                              mandatory_hyps=hyps)
                else:db._save(label,kind,expr,hyps,dv)
        require(not db.stack,'unclosed scope')
        return db

    @classmethod
    def load(cls,path):
        """Read local Metamath source and expand local $[ file $] includes.
        Explicitly no HTTP includes, absolute paths or traversal outside the root.
        """
        path=Path(path).resolve()
        base=path.parent
        included=set()
        def expand(p):
            p=p.resolve()
            require(p.is_relative_to(base), 'include outside frozen source directory')
            require(p not in included, 'duplicate or cyclic Metamath include')
            included.add(p)
            data=p.read_text(encoding='utf8')
            # Ignore comments when recognizing includes, while retaining comments
            # in the returned text for from_text to remove normally.
            pattern=r'\$\((?:.|\n)*?\$\)|\$\[\s*([^\s]+)\s*\$\]'
            def sub(m):
                if m.group(1) is None: return m.group(0)
                name=m.group(1)
                require('://' not in name and not Path(name).is_absolute(),'non-local Metamath include')
                return '\n'+expand(p.parent/name)+'\n'
            return re.sub(pattern,sub,data)
        return cls.from_text(expand(path),name=str(path))

    def verify(self,goal,proof,*,active_dv=frozenset(),legal_before=None,expected_hyps=(),extra_hyps=None,mandatory_hyps=None):
        """Verifies an uncompressed proof. Supports an external theorem with
        declared target + frozen active $d; untrusted intermediate results aren't reusable.
        expected_hyps is intentionally empty for external closed goal proofs.
        """
        goal=tuple(goal)
        proof=list(proof)
        # Ordinal gate avoids rebuilding a huge allowed-label set for every
        # compressed theorem while a large frozen database is being imported.
        extra_hyps={} if extra_hyps is None else {k:tuple(v) for k,v in extra_hyps.items()}
        require(all(k not in self.statements for k in extra_hyps),'hypothesis label collides with database')
        require(all(v and v[0] in self.constants for v in extra_hyps.values()),'invalid extra hypothesis')
        active_dv=frozenset(tuple(sorted(pair)) for pair in active_dv)
        vars=self.variables
        stack=[]
        saved=[]
        if proof and proof[0]=='(':
            require(mandatory_hyps is not None, 'compressed proof requires declared mandatory hypotheses')
            actions=decode_compressed(proof, mandatory_hyps)
        else:
            actions=(('label',label) for label in proof)
        for pos,action in enumerate(actions,1):
            if action[0]=='save':
                require(stack, f'compressed Z with empty stack at step {pos}')
                saved.append(stack[-1])
                continue
            if action[0]=='reuse':
                idx=action[1]
                require(0<=idx<len(saved), f'bad saved proof index {idx} at step {pos}')
                stack.append(saved[idx])
                continue
            label=action[1]
            if label in extra_hyps:
                stack.append(extra_hyps[label])
                continue
            require(label in self.statements and (legal_before is None or
                    self.statements[label].ordinal<=legal_before),
                    f'unknown or future step label {label} at step {pos}')
            st=self.statements[label]
            if st.kind in ('$f','$e'):
                require((st.kind=='$f' and label in self.active_f) or
                        (st.kind=='$e' and label in expected_hyps),
                        f'inactive hypothesis {label}')
                stack.append(st.expr)
                continue
            k=len(st.hyps)
            require(len(stack)>=k, f'stack underflow at {label}')
            args=stack[-k:] if k else []
            if k:del stack[-k:]
            mapping={}
            for h_label,arg in zip(st.hyps,args):
                h=self.statements[h_label]
                if h.kind!='$f':continue
                require(arg and arg[0]==h.expr[0],f'floating type mismatch at {label}: {h_label}')
                var=h.expr[1]
                require(var not in mapping,'duplicate floating variable')
                mapping[var]=arg[1:]
            def sub(expression):
                out=[]
                for tok in expression:
                    if tok in vars:
                        require(tok in mapping, f'unmapped variable {tok} at {label}')
                        out.extend(mapping[tok])
                    else:out.append(tok)
                return tuple(out)
            for h_label,arg in zip(st.hyps,args):
                h=self.statements[h_label]
                if h.kind=='$e':
                    require(arg==sub(h.expr),f'essential hypothesis mismatch at {label}')
            for a,b in st.dv:
                lhs={v for v in mapping[a] if v in vars}
                rhs={v for v in mapping[b] if v in vars}
                for x in lhs:
                    for y in rhs:
                        require(x!=y and tuple(sorted((x,y))) in active_dv, f'DV violation at {label}: {x},{y}')
            stack.append(sub(st.expr))
        require(len(stack)==1 and stack[0]==goal,
                f'goal mismatch: stack={stack[-1:] if stack else []}, expected={goal}')
        return True

    def digest(self):
        payload='\n'.join(f'{k}:{s.kind}:{s.expr}:{s.hyps}:{sorted(s.dv)}' for k,s in self.statements.items())
        return hashlib.sha256(payload.encode()).hexdigest()
