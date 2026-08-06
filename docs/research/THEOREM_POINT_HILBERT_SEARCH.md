# Theorem-Point Hilbert Search After Training

**Author/director:** Brian Tenneson  
**Status:** working mathematical specification  
**Date:** 2026-08-06

## 1. Purpose

The ultimate purpose of the construction is not merely to prove a fixed target after training. It is to search for theorems.

Training produces a search policy, representation, premise-ranking model, novelty model, or resource-allocation rule. After training is frozen, Data-ATP enters a theorem-discovery phase. In that phase:

- the formal system is fixed;
- the hypothesis or axiom set is fixed;
- the verifier is fixed and external;
- the trained policy may order legal search, but it cannot decide truth;
- every newly verified consequence is recorded as a theorem-point;
- the accumulated verified consequence set becomes the moving frontier from which later theorems are generated.

Thus training learns navigation. The post-training run performs theorem search.

## 2. Effective syntax and rational theorem addresses

Let

\[
F=(x,y,z)
\]

be an effectively presented formal system. Assume that well-formedness is decidable. Then there is a computable one-to-one enumeration

\[
\nu_F:\mathbb N\to y,
\qquad
j\mapsto \varphi_j,
\]

of all well-formed formulas.

Brian Tenneson's explicit surjection

\[
s:\mathbb N\twoheadrightarrow\mathbb Q
\]

can be composed with a fixed computable bijection or surjection from \(\mathbb Q\) onto \(\mathbb Q\cap[0,1]\). Write the resulting map as

\[
q:\mathbb N\twoheadrightarrow \mathbb Q\cap[0,1].
\]

A formula may then receive a rational geometric address, for example

\[
a_F(\varphi_j)=q(j).
\]

For tuples of formulas, use product addresses:

\[
a_F(\varphi_{j_1},\ldots,\varphi_{j_k})
=
(q(j_1),\ldots,q(j_k))
\in
(\mathbb Q\cap[0,1])^k.
\]

The role of the rational cube is representational. The cube is not identified literally with the consequence set. Instead, theorem-related objects are embedded into a countable dense subset of the cube.

## 3. Inference-rule geometry

Let

\[
z=\{r_1,\ldots,r_m\},
\qquad
\operatorname{arity}(r_i)=k_i.
\]

There are three related dimensions.

### 3.1 Intrinsic rule dimension

The rule \(r_i\) naturally acts on

\[
(\mathbb Q\cap[0,1])^{k_i},
\]

because one coordinate is needed for each premise position.

### 3.2 Orthogonal ambient dimension

Define

\[
K=\sum_{i=1}^{m}k_i.
\]

Partition the coordinates of \([0,1]^K\) into blocks of lengths \(k_1,\ldots,k_m\). Embed the premise-address space of each rule into its own orthogonal coordinate face. Then \(K\) is an ambient orthogonality dimension, not necessarily the dimension in which every search step must run.

### 3.3 Intrinsic action complex

The preferred intrinsic search object is

\[
\mathcal A_F
=
\bigsqcup_{i=1}^{m}
(\mathbb Q\cap[0,1])^{k_i}.
\]

An element is a tagged tuple

\[
(i;u_1,\ldots,u_{k_i}),
\]

where \(i\) selects the inference rule and the coordinates select candidate premises.

This avoids searching the meaningless full product

\[
[0,1]^{k_1+\cdots+k_m},
\]

whose points simultaneously select premises for every rule. The rules remain geometrically orthogonal while their logical conclusions may still interact through later inference.

## 4. Hilbert traversal

For every \(d>1\), let

\[
H_d:[0,1]\twoheadrightarrow[0,1]^d
\]

be a continuous space-filling curve. Since

\[
(\mathbb Q\cap[0,1])^d\subseteq[0,1]^d,
\]

surjectivity implies that every rational premise-address tuple has at least one preimage under \(H_d\).

The limiting curve is a mathematical coverage object, not a finite physical or computational trajectory. Actual search uses finite approximants

\[
H_{d,0},H_{d,1},H_{d,2},\ldots,
\]

which traverse successively finer dyadic cells.

For rule \(r_i\), Data-ATP runs a Hilbert traversal on dimension \(k_i\). A scheduler dovetails among the rule-specific traversals. Therefore the theorem-search path is a path through the disjoint union of rule cubes, or through their orthogonal embedding in \([0,1]^K\).

## 5. The theorem-search probe

At search time \(t\), let

\[
P_t=(\psi_1,\ldots,\psi_{\ell_t})
\]

be the accumulated verified derivation record, and let

\[
C_t=\{\psi_1,\ldots,\psi_{\ell_t}\}
\]

be the corresponding verified consequence set.

The probe is not merely one formula and not merely one point. Define

\[
\mathfrak p_t
=
(P_t,C_t,\partial C_t,u_t),
\]

where:

- \(P_t\) is the complete verified derivation history;
- \(C_t\) is the current theorem set;
- \(\partial C_t\) is the current legal inference frontier;
- \(u_t\in\mathcal A_F\) is the active Hilbert inference address.

The statement that the probe contains the entire initial segment of the proof is expressed by monotonicity:

\[
P_t\preceq P_{t+1},
\qquad
C_t\subseteq C_{t+1}.
\]

The probe may revisit geometric neighborhoods or rule families, but verified proof history is never erased.

## 6. Theorem-points

A theorem-point is not merely a rational point that happens to be visited. It is a verified conclusion together with its address and certificate.

Define a theorem-point record as

\[
\Theta
=
(\varphi,a_F(\varphi),\pi,V,\tau),
\]

where:

- \(\varphi\in y\) is the conclusion;
- \(a_F(\varphi)\in\mathbb Q\cap[0,1]\), or in a higher-dimensional theorem embedding, is its declared address;
- \(\pi\) is a formal proof certificate;
- \(V\) is the verifier identity and version;
- \(\tau\) is the complete provenance transaction.

The verified theorem-point set after budget \(B\) is

\[
\mathcal T_F(\Gamma;B)
=
\{\Theta:\Theta\text{ was externally verified within budget }B\}.
\]

The operational objective is to maximize useful growth of \(\mathcal T_F(\Gamma;B)\), subject to soundness, novelty, proof quality, and resource constraints.

## 7. Decoding one Hilbert address

Freeze the current consequence set \(C_t\) during one search epoch. Enumerate it canonically as

\[
C_t=\{\chi_1,\ldots,\chi_N\}.
\]

At dyadic resolution \(q\), divide each coordinate into \(M=2^q\) bins. Define

\[
d_{N,M}(a)
=
1+\left\lfloor\frac{aN}{M}\right\rfloor,
\qquad
0\leq a<M.
\]

For a rule \(r_i\) of arity \(k_i\), a Hilbert cell indexed by

\[
(a_1,\ldots,a_{k_i})
\]

decodes to the candidate inference

\[
r_i\bigl(
\chi_{d_{N,M}(a_1)},\ldots,
\chi_{d_{N,M}(a_{k_i})}
\bigr).
\]

The system checks legality before heuristic value. A new legal conclusion enters a staging buffer, is independently verified, and only then becomes a theorem-point and a member of the next consequence frontier.

## 8. Straight motion and turning

The geometric language should be defined operationally rather than left metaphorical.

### 8.1 Going straight

A straight segment means that the active rule remains fixed and the Hilbert traversal continues locally within the same rule cube without changing its current coordinate direction.

Logically, this means continuing a local family of candidate applications of the same inference rule while varying one premise-address coordinate and holding the other premise slots fixed over that local segment.

For a unary rule, straight motion is especially literal: successive points test successive candidate inputs to the same rule.

For a rule of arity greater than one, straight motion means varying one selected premise position while the other positions remain locally fixed.

### 8.2 Turning within one rule cube

A turn inside the same \(k_i\)-dimensional rule cube changes the active coordinate direction. Logically, the search changes which premise position is being varied.

For a binary rule:

- movement parallel to the first axis varies the first premise while locally fixing the second;
- movement parallel to the second axis varies the second premise while locally fixing the first;
- a turn exchanges which premise slot is currently being explored.

Thus a turn can correspond to a previously produced theorem becoming included as a different input position in a multi-premise inference.

### 8.3 Turning between orthogonal rule faces

A transition from one orthogonal rule face to another means changing the inference rule itself.

This captures Brian Tenneson's proposed interpretation that turning may correspond either to entering another premise dimension of a rule with arity greater than one or to changing to a different inference rule altogether.

### 8.4 Logical advance

The geometric path can turn, but the verified derivation advances monotonically:

\[
C_t\subseteq C_{t+1}.
\]

This is the theorem-search analogue of a probe that never reverses its accumulated discovery.

## 9. Post-training theorem discovery algorithm

A theorem-discovery epoch is:

1. Freeze the trained model, formal library, verifier, budgets, and random seed policy.
2. Freeze the current verified consequence set \(C_e\).
3. Build its canonical enumeration.
4. Allocate a finite budget among rule faces.
5. Traverse finite Hilbert approximants on those faces.
6. Decode visited cells into premise tuples.
7. Check rule applicability and all side conditions.
8. Rank only among legal candidates.
9. Externally verify every proposed certificate.
10. Add each previously unknown verified conclusion as a theorem-point.
11. Preserve complete provenance, including failures and duplicates.
12. Start the next epoch from the enlarged consequence set.

Training may influence steps 4 and 8. It may not alter steps 7 or 9.

## 10. Budget accounting

At resolution \(q\), complete coverage of rule \(r_i\)'s dyadic premise grid requires

\[
E_{i,q}=2^{qk_i}
\]

cell evaluations.

A complete all-rule pass requires

\[
E_q
=
\sum_{i=1}^{m}2^{qk_i}.
\]

The cumulative nominal budget through level \(Q\) is

\[
B_Q
=
\sum_{q=0}^{Q}\sum_{i=1}^{m}2^{qk_i}
=
\sum_{i=1}^{m}
\frac{2^{k_i(Q+1)}-1}{2^{k_i}-1},
\]

for positive arities.

Given total budget \(B\), define

\[
Q_*(B)
=
\max\{Q:B_Q\leq B\}.
\]

The interruption certificate is:

> Every rule-specific premise grid has been completely searched through resolution \(Q_*(B)\), regardless of how far the next incomplete pass progressed.

The complete run report should include:

- last completed global resolution;
- per-rule next-level completion fraction;
- legal applications tested;
- duplicate conclusions;
- new theorem-points;
- verified proofs rejected by novelty filters but retained in the archive;
- expansions, wall time, memory, and verifier time;
- learned-policy exceptions and returns to the coverage schedule.

## 11. Completeness claim under dovetailing

Assume:

1. the formal system has finitely many finitary rules;
2. rule applicability is decidable;
3. the WFF and current-consequence enumerations are effective;
4. every rule face and every finite resolution is eventually completed;
5. every legal new conclusion is eventually admitted to a later frozen frontier;
6. certificates are checked by a sound verifier.

Then every formula in

\[
\operatorname{Con}_F(\Gamma)
\]

is eventually added to the verified theorem-point set.

The proof is by induction on the lines of any finite proof. Once all premises of one proof line have entered some frozen frontier, a sufficiently fine complete Hilbert pass visits a cell decoding to that ordered premise tuple for the required rule. The conclusion is therefore generated and, if valid, eventually admitted.

This is a completeness theorem for theorem enumeration, not an efficiency theorem.

## 12. What training adds

The Hilbert schedule supplies a proof-covering baseline. Training may improve the order in which cells, faces, resolutions, theorem families, or promising local neighborhoods are visited.

A trained policy can propose:

- which rule face receives more budget;
- which Hilbert subcells are locally promising;
- which newly found theorem has high reuse value;
- which premise tuples deserve immediate bounded follow-up;
- when to refine resolution;
- when to return to coarse global coverage.

But the wrapper must preserve eventual coverage. Otherwise training may increase short-run yield while permanently excluding entire theorem families.

The research question is therefore not merely whether learning discovers more theorems. It is:

\[
\text{How much useful verified theorem growth can learning buy per expansion}
\]

while retaining a declared coverage guarantee?

## 13. Core synthesis

The program now links four constructions:

\[
\mathbb N\twoheadrightarrow\mathbb Q
\]

provides explicit rational addresses;

\[
\mathbb N\to\operatorname{WFF}(F)
\]

provides effective logical objects;

\[
H_d:[0,1]\twoheadrightarrow[0,1]^d
\]

provides continuous and finite-resolution coverage orderings;

and

\[
\Gamma\subseteq C_0\subseteq C_1\subseteq\cdots
\]

provides monotone verified theorem growth.

The resulting interpretation is:

> Data-ATP is a budgeted, trained, accountable probe whose body is its complete verified derivation history, whose frontier is the set of legal next inferences, whose geometric motion schedules premise tuples, and whose discoveries are externally verified theorem-points.
