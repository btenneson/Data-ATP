# Budget-balanced Hilbert-derived coverage paths

**Author:** Brian Tenneson  
**Status:** working research specification, August 2026

## Core physical model

Let the region be the n-cube `Omega_n = [0,L]^n`, `n > 1`. A positive-speed probe follows a continuous path `gamma`; its travel budget is arclength `B`. Define coverage defect

`delta(B) = sup_{x in Omega_n} dist(x, gamma([0,B]))`.

A sensor of radius `rho` maps the whole region when `delta(B) <= rho`.

The exact limiting Hilbert curve is not a finite-speed route: any rectifiable curve has zero n-dimensional volume for `n > 1`. A physical vehicle must traverse finite approximants.

At level `m`, dyadically partition the cube into

- `N_m = 2^(m n)` cells,
- side `h_m = L / 2^m`.

For a face-continuous Hilbert ordering of cell centers, the ideal stage length is

`ell_m = (N_m - 1) h_m = L(2^(m(n-1)) - 2^(-m))`.

After completing the stage,

`delta <= sqrt(n) L / 2^(m+1)`.

## Part I - two dimensions and the interruption guarantee

Execute complete Hilbert passes at levels `0,1,2,...`, alternating orientation so each new pass begins near the previous endpoint. This deliberately repeats coarse coverage before refining.

In two dimensions,

`ell_m^(2) = L(2^m - 2^(-m))`,

`B_m^(2) = L(2^(m+1) - 3 + 2^(-m))`.

For interruption budget `B`, let

`m_*(B) = max{m : B_m^(2) <= B}`.

Then

`delta(B) <= sqrt(2) L / 2^(m_*(B)+1)`.

A partial fine pass can never erase the last completed coarse guarantee. This is the central "anytime" contribution.

## Part II - three dimensions and partial runs

A 3D implementation may use either layered 2D passes or a face-continuous voxel Hilbert ordering.

For voxels,

`ell_m^(3) = L(4^m - 2^(-m))`,

`B_m^(3) = L((4^(m+1)-7)/3 + 2^(-m))`,

`delta(B_m) <= sqrt(3)L / 2^(m+1)`.

Thus `delta(B) = O(sqrt(L^3/B))`.

If level `m` is complete and level `q=m+1` is underway, the ideal number of fine voxel representatives visited is

`k_3(B) = min(8^q, 1 + floor((B-B_m^(3))/h_q))`,

and fine-stage fraction is `p_q(B)=k_3(B)/8^q`. This progress fraction is distinct from the rigorous global coarse bound.

## Part III - n dimensions

Absolute signed axis directions are

`D_n = {+e_1,-e_1,...,+e_n,-e_n}`,

so `|D_n|=2n`. Given a current axis heading and excluding immediate reversal, the next-command count is

`1 + 2(n-1) = 2n-1`.

The cumulative ideal travel budget through level `m` is

`B_m^(n) = L[(2^((n-1)(m+1))-1)/(2^(n-1)-1) - 2 + 2^(-m)]`.

The interruption bound is

`delta(B) <= sqrt(n)L / 2^(m_n(B)+1)`,

where `m_n(B)=max{m:B_m^(n)<=B}`.

Eliminating `m` gives

`delta(B) = O((L^n/B)^(1/(n-1)))`.

A covering-number argument yields the same necessary exponent: a length-`B` curve's `rho`-neighborhood can be covered by at most about `B/rho` balls of radius `2rho`, so covering volume `L^n` requires `B = Omega(L^n/rho^(n-1))`.

### Turning-radius warning

A naive local rounding of every Hilbert corner with minimum radius `R_min` needs roughly `2R_min <= h_m`. Therefore simple cell-local rounding cannot be refined indefinitely at fixed `R_min`; finer implementation needs nonlocal turns, boundary excursions, or another smooth incremental coverage curve.

## Part IV - ATP budgets

Let `S` be a proof-state space with a declared metric or pseudometric `d`, and let `R` be the relevant region. After `E` legal expansions producing states `s_0,...,s_E`, define

`Delta(E) = sup_{x in R} min_{j<=E} d(x,s_j)`.

Recursively partition `R`; complete a representative expansion obligation in every coarse cell before deep refinement. If each level has `M` children per cell and diameter contracts by `lambda`, then

`Delta(E) = O(E^(-alpha))`,

`alpha = log(1/lambda)/log(M)`.

For a dyadic effective `d`-dimensional feature cube, `M=2^d`, `lambda=1/2`, and

`Delta(E)=O(E^(-1/d))`.

This differs from the physical exponent because expansions count sampled proof states rather than continuous connector length.

## Accountable local exceptions

The coverage schedule is a soft strategy, not a hard theorem. A transient proof signal may justify a bounded deviation if:

1. the action is legal;
2. no hard invariant or verifier boundary is changed;
3. evidence and expected gain meet frozen thresholds;
4. the exception fits outside a protected reserve;
5. a return point is named;
6. the complete action and outcome are logged;
7. a post-action self-report is filed even after success.

## Prior-art boundary

Using Hilbert or other space-filling curves for coverage is not itself new. Relevant prior work includes Hilbert (1891), Dubins (1957), Butz (1969, 1971), Choset (2001), Ramamoorthy-Rajagopal-Wenzel (2008), Galceran-Carreras (2013), Nair-Sinha-Vachhani (2017), Joshi-Bhatt-Sinha (2019), Wakode-Sinha (2022, 2023), and Haverkort's higher-dimensional Hilbert studies. Any publication claim must focus on the specific coarse-to-fine interruption certificate, constrained implementation, comparison with incremental low-discrepancy curves, or experimentally validated ATP translation.
