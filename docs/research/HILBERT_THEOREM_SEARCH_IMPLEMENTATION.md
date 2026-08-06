# Hilbert Theorem-Search Implementation Specification

## Goal

Implement a Python theorem-discovery engine for a finitary formal system

\[
F=(x,y,z),\qquad z=\{r_1,\ldots,r_m\},
\]

where rule \(r_i\) has arity \(k_i\). The engine must use finite approximants to Hilbert space-filling curves to order candidate premise tuples under a frozen expansion budget. It must preserve verifier sovereignty, complete transaction logs, and a monotone theorem database.

The learned component may alter order and allocation after training. It may not alter legality, the verifier, or the declared budget.

## 1. Intrinsic inference-address space

For a frozen verified theorem set \(C\subseteq y\), the intrinsic action space is the coproduct

\[
\mathcal A_F(C)=\bigsqcup_{i=1}^{m} C^{k_i}.
\]

An element is a tagged tuple

\[
(i;a_1,\ldots,a_{k_i}),
\]

meaning: attempt rule \(r_i\) on ordered premises \((a_1,\ldots,a_{k_i})\).

The coproduct prevents unrelated rules from creating meaningless Cartesian products. The optional ambient orthogonal dimension is

\[
K=\sum_{i=1}^{m}k_i.
\]

Each rule cube \([0,1]^{k_i}\) may be embedded into its own coordinate block of \([0,1]^K\), with all other coordinates fixed. \(K\) is an embedding dimension, not the intrinsic dimension of every inference.

## 2. Rational and line-number addressing

Brian Tenneson's map

\[
r:\mathbb N_+\twoheadrightarrow\mathbb Q
\]

and least-preimage section

\[
s:\mathbb Q\to\mathbb N_+,
\qquad r(s(q))=q,
\]

supply explicit rational addresses and canonical line numbers.

Restrict to the rational unit interval by

\[
u(n)=
\begin{cases}
r(n),&0\le r(n)\le1,\\
0,&\text{otherwise}.
\end{cases}
\]

Then \(u:\mathbb N_+\twoheadrightarrow \mathbb Q\cap[0,1]\), and for every \(q\in\mathbb Q\cap[0,1]\),

\[
u(s(q))=q.
\]

Let Tenneson's pairing polynomial be

\[
\pi(a,b)=\frac{(a+b-1)(a+b-2)}2+a.
\]

Recursively define

\[
\pi_1(a_1)=a_1,
\qquad
\pi_n(a_1,\ldots,a_n)=\pi\!\left(a_1,\pi_{n-1}(a_2,\ldots,a_n)\right).
\]

Its inverse recursively decodes one line number \(L\) into \((a_1,\ldots,a_n)\in\mathbb N_+^n\) using the inverse-pair coordinates A002260 and A004736.

Thus

\[
R_n(L)=\bigl(u(a_1),\ldots,u(a_n)\bigr)
\]

defines an explicit surjection

\[
R_n:\mathbb N_+\twoheadrightarrow(\mathbb Q\cap[0,1])^n.
\]

A canonical right inverse is

\[
S_n(q_1,\ldots,q_n)=\pi_n\bigl(s(q_1),\ldots,s(q_n)\bigr),
\]

so

\[
R_n(S_n(\mathbf q))=\mathbf q.
\]

This rational-cube line numbering is a global address layer. The finite Hilbert step number below is a separate operational index.

## 3. WFF line numbers and theorem-points

Fix an effective one-to-one enumeration

\[
g\longmapsto\varphi_g
\]

of the well-formed formulas of the formal language. A Gödel number or WFF line number answers which formula is being addressed; it does not establish theoremhood.

A theorem-point is created only after verification:

\[
\Theta=(g,\varphi_g,\pi,V,\text{provenance}),
\]

where \(\pi\) is a proof certificate and \(V(\pi,g)=1\).

For visualization, a WFF line number may be assigned a rational point, but the implementation must preserve the line number and formula as the unique identity. A surjective rational map alone must not be used as a unique identifier because it may have collisions.

## 4. Finite Hilbert traversal of one rule cube

Freeze an epoch theorem list

\[
C_e=(\theta_0,\ldots,\theta_{M-1}).
\]

Let

\[
p=\lceil\log_2 M\rceil,
\qquad
N=2^p.
\]

For a rule of arity \(k\), use a standard discrete \(k\)-dimensional Hilbert index map

\[
H_{k,p}:\{0,\ldots,N^k-1\}\to\{0,\ldots,N-1\}^k.
\]

Each Hilbert step \(h\) gives coordinates

\[
H_{k,p}(h)=(j_1,\ldots,j_k).
\]

If every \(j_t<M\), decode the point as the ordered premise tuple

\[
(\theta_{j_1},\ldots,\theta_{j_k}).
\]

If some \(j_t\ge M\), the point is padding and produces no rule application. Padding permits an exact power-of-two Hilbert grid without duplicating valid tuples.

Every ordered tuple in \(C_e^k\) appears exactly once among the nonpadding Hilbert cells.

## 5. Straight motion and turning

Successive cells of a discrete Hilbert path are face-adjacent. Therefore one coordinate changes by one grid unit at each step.

Within the cube of rule \(r_i\):

- **straight motion** means consecutive Hilbert steps continue changing the same coordinate axis; semantically, the same premise slot is varied while the other premise slots remain locally fixed;
- **a turn within the cube** means the changed coordinate axis switches; semantically, the search switches which premise position is being varied;
- **a coproduct turn** means the scheduler switches from rule component \(i\) to rule component \(j\); semantically, the inference rule changes.

This gives an exact computational meaning to straight, left/right/up/down, and higher-dimensional turning. Directions are coordinate-axis changes, not informal metaphors.

## 6. Epoch semantics

A complete epoch freezes \(C_e\), traverses all rule components, stages every novel verified conclusion, and then appends the staged conclusions in deterministic order.

Define the direct-consequence operator

\[
D_F(C)=C\cup\{r_i(\bar a):\bar a\in C^{k_i},\ r_i(\bar a)\text{ is defined}\}.
\]

If every valid tuple on every rule face is attempted and every legal novel conclusion is accepted, then

\[
C_{e+1}=D_F(C_e).
\]

Starting at \(C_0=\Gamma\), complete epochs yield

\[
C_e=D_F^e(\Gamma),
\qquad
\bigcup_{e=0}^{\infty}C_e=\operatorname{Con}_F(\Gamma).
\]

Thus Hilbert search changes the order in which each finite consequence layer is examined; it does not alter logical closure.

## 7. Expansion budget

One **expansion** is one attempted rule application on one valid decoded premise tuple. Padding visits are counted separately as address visits.

For frozen theorem-set size \(M\), the exact number of valid candidate tuples in a complete epoch is

\[
E(C)=\sum_{i=1}^{m}M^{k_i}.
\]

The number of Hilbert grid cells, including padding, is

\[
A(C)=\sum_{i=1}^{m}N^{k_i},
\qquad N=2^{\lceil\log_2 M\rceil}.
\]

A run budget must declare at least:

- maximum expansions;
- maximum address visits;
- wall-clock ceiling;
- memory ceiling;
- verifier budget;
- protected reserve.

A partial-run certificate records, for each rule component:

\[
(h_i,N^{k_i},e_i,v_i),
\]

where \(h_i\) is Hilbert cells visited, \(e_i\) is valid premise tuples attempted, and \(v_i\) is verified novel conclusions found.

## 8. Coarse-to-fine mode

Before the exact level \(p\), levels \(q<p\) may partition the theorem indices into \(2^q\) bins per coordinate and choose one representative per bin. These passes are heuristic previews and do not exhaust \(C_e^{k_i}\).

The exact completeness certificate for epoch \(e\) is issued only after every rule face completes level

\[
p=\lceil\log_2|C_e|\rceil
\]

with padding as specified above.

An interrupted fine pass cannot erase the last completed coarse certificate, but only an exact completed epoch licenses the equality \(C_{e+1}=D_F(C_e)\).

## 9. Trained post-training policy

After training, Data-ATP searches for newly verified theorems. A frozen learned policy may:

- choose the order of rule components;
- choose Hilbert orientations and starting corners;
- allocate budget among components;
- prioritize promising subcubes;
- request bounded evidence-triggered exceptions;
- decide when to run coarse previews.

It may not:

- invent illegal rule applications;
- declare theoremhood;
- modify the verifier;
- alter sealed benchmarks;
- exceed the declared budget;
- permanently discard cells in a run advertised as complete.

The wrapper supplies fairness and completeness; the learned policy supplies navigation.

## 10. Probe state

The computational probe at time \(t\) is

\[
\mathfrak p_t=(C_t,P_t,Q_t,i_t,q_t,h_t,B_t),
\]

where:

- \(C_t\) is the monotone verified theorem database;
- \(P_t\) is the provenance/proof forest for all accepted theorems;
- \(Q_t\) is the remaining frontier of tagged Hilbert cells;
- \(i_t\) is the active rule component;
- \(q_t\) is the active resolution;
- \(h_t\) is the Hilbert step index;
- \(B_t\) is the remaining budget vector.

For a target theorem, the relevant proof is the predecessor chain inside \(P_t\). For theorem discovery, the probe is the entire verified state and proof forest, not merely the current coordinate.

## 11. Python reference loop

```python
def run_epoch(system, verified, expansion_budget, scheduler, verifier):
    frozen = tuple(verified.formulas())
    size = len(frozen)
    bits = max(0, (size - 1).bit_length())
    side = 1 << bits
    staged = {}

    cursors = {
        rule.name: HilbertCursor(dim=rule.arity, bits=bits)
        for rule in system.rules
    }

    while expansion_budget > 0 and not all(c.done for c in cursors.values()):
        rule = scheduler.choose_rule(system.rules, cursors, frozen)
        point = cursors[rule.name].next_point()

        if any(index >= size for index in point):
            log_padding_visit(rule, point)
            continue

        premises = tuple(frozen[index] for index in point)
        expansion_budget -= 1
        log_expansion(rule, point, premises)

        for candidate in rule.apply(premises):
            if not system.legal(rule, premises, candidate):
                continue
            certificate = build_certificate(rule, premises, candidate, verified)
            if verifier.accepts(certificate, candidate):
                staged.setdefault(candidate, certificate)

    verified.append_staged_in_canonical_order(staged)
    return make_partial_or_complete_certificate(cursors, staged, expansion_budget)
```

## 12. First implementation milestone

The first runnable experiment should use a tiny finite formal system with at least:

- one unary rule;
- one binary rule;
- one rule with arity greater than two;
- decidable syntax and legality;
- a trusted independent verifier;
- known finite closure layers for regression tests.

Required tests:

1. Hilbert bijection on every tested \((k,p)\) grid.
2. Successive Hilbert cells differ in exactly one coordinate by one unit.
3. Every valid ordered premise tuple is attempted exactly once in a complete epoch.
4. Padding cells never create expansions.
5. Complete epoch output equals direct exhaustive closure output.
6. Partial-run certificate reproduces the exact stopping point.
7. Learned reordering changes order but not the complete epoch result.
8. No unverified conclusion enters trusted storage.
9. Re-running with the same seed and frozen policy reproduces the transaction log.
10. Target mode returns an independently verifiable proof chain.

## Final statement

The implemented object is not a continuous physical curve pretending to prove theorems. It is a reproducible, budgeted Hilbert ordering of the coproduct of rule-arity premise spaces. Every visited valid cell decodes to one candidate inference. Every accepted conclusion becomes a verified theorem-point with provenance. Repeated complete epochs compute the deductive closure, while training changes which parts of the same legally defined search space are explored first.
