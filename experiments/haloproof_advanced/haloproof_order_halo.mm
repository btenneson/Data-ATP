$(
  HaloProof order/halo development extension.

  This file is concatenated AFTER the exact frozen set.mm snapshot by the
  HaloProof campaign.  It introduces no new axiom.  The concrete benchmark is

      P = Poly1(RRfld)
      H = Frac(P).

  The first six development theorems below have now been independently verified
  by the local project verifier against the frozen set(3).mm snapshot with
  SHA-256

      1016D7EDB0508ABDE0FE240BB5243E588C5067F8CB10EE6E1CC5733FC05ACDB5

  Candidate lemmas are promoted to verified status only after the campaign
  verifier accepts them on that same frozen database.

  Remaining theorem families, in order:

  ES1c nonzero polynomial has a nonzero coefficient / nonempty support
  ES1d least nonzero exponent exists
  ES1e define least-nonzero-coefficient sign for nonzero Poly1(RRfld)
  ES2  prove polynomial eventual-sign multiplication compatibility
  ES3  lift sign to Frac(P) and prove representative invariance via fracerl
  ES4  prove strict total order and compatibility with field operations
  ES5  package H with that order as an ordered field
  HA1  identify the embedded variable t and prove 0 < t
  HA2  prove t < r for every positive real constant r
  HA3  prove t is a nonzero infinitesimal
  HA4  define the exact two-sided halo I
  CA1  prove r |-> r t is one-to-one from RR into I
  CA2  prove H ~~ RR from finite real coefficient data
  CA3  prove I ~<_ RR and finish I ~~ RR by sbth

  A comment-only obligation is not a theorem and is never counted as one.
$)

$( The real-number structure used by HaloProof is a field. $)
hprefld $p |- RRfld e. Field $= refld $.

$( The real-number field is therefore an integral domain. $)
hpridom $p |- RRfld e. IDomn $=
  crefld cfield wcel
  crefld cidom wcel
  refld
  crefld fldidom
  ax-mp
$.

$( The native univariate polynomial ring over RRfld is an integral domain. $)
hppolyidom $p |- ( Poly1 ` RRfld ) e. IDomn $=
  crefld cidom wcel
  crefld cpl1 cfv cidom wcel
  hpridom
  crefld cpl1 cfv
  crefld
  crefld cpl1 cfv eqid
  ply1idom
  ax-mp
$.

$( The concrete rational-function carrier used by HaloProof is a field. $)
hpfracfield $p |- ( Frac ` ( Poly1 ` RRfld ) ) e. Field $=
  crefld cpl1 cfv cidom wcel
  crefld cpl1 cfv cfrac cfv cfield wcel
  hppolyidom
  crefld cpl1 cfv cidom wcel
  crefld cpl1 cfv
  crefld cpl1 cfv cidom wcel id
  fracfld
  ax-mp
$.

$( ES1a: coefficients of a concrete HaloProof polynomial form a map from NN0
   into the base set of the real field. $)
hpcoe1map $p |- ( F e. ( Base ` ( Poly1 ` RRfld ) ) ->
  ( coe1 ` F ) : NN0 --> ( Base ` RRfld ) ) $=
  cF cco1 cfv
  crefld cpl1 cfv cbs cfv
  crefld cpl1 cfv
  crefld
  cF
  crefld cbs cfv
  cF cco1 cfv eqid
  crefld cpl1 cfv cbs cfv eqid
  crefld cpl1 cfv eqid
  crefld cbs cfv eqid
  coe1f
$.

$( ES1b: the coefficient vector of a concrete HaloProof polynomial has finite
   support relative to the real-field zero. $)
hpcoe1fsupp $p |- ( F e. ( Base ` ( Poly1 ` RRfld ) ) ->
  ( coe1 ` F ) finSupp ( 0g ` RRfld ) ) $=
  cF cco1 cfv
  crefld cpl1 cfv cbs cfv
  crefld cpl1 cfv
  crefld
  cF
  crefld c0g cfv
  cF cco1 cfv eqid
  crefld cpl1 cfv cbs cfv eqid
  crefld cpl1 cfv eqid
  crefld c0g cfv eqid
  coe1sfi
$.

$( ES1c candidate, generic form: a nonzero univariate polynomial over a ring
   has at least one nonzero coefficient.  The witness is its native degree:
   deg1nn0cl puts that degree in NN0 and deg1ldg says its coefficient is
   nonzero.  This theorem is kept generic so later HaloProof lemmas can reuse
   it without reproving the ring-level fact. $)
${
  $d n A $.  $d n B $.  $d n D $.  $d n F $.  $d n P $.  $d n R $.
  $d n Y $.  $d n .0. $.
  hpcoe1nzex.d $e |- D = ( deg1 ` R ) $.
  hpcoe1nzex.p $e |- P = ( Poly1 ` R ) $.
  hpcoe1nzex.z $e |- .0. = ( 0g ` P ) $.
  hpcoe1nzex.b $e |- B = ( Base ` P ) $.
  hpcoe1nzex.y $e |- Y = ( 0g ` R ) $.
  hpcoe1nzex.a $e |- A = ( coe1 ` F ) $.
  hpcoe1nzex $p |- ( ( R e. Ring /\ F e. B /\ F =/= .0. ) ->
    E. n e. NN0 ( A ` n ) =/= Y ) $=
  cR crg wcel cF cB.wceq wcel cF c.0 wne w3a
  cF cD cfv cn0 wcel
  cF cD cfv cA.wceq cfv cY wne wa
  vn cv cA.wceq cfv cY wne
  vn cn0 wrex
  cR crg wcel cF cB.wceq wcel cF c.0 wne w3a
  cF cD cfv cn0 wcel
  cF cD cfv cA.wceq cfv cY wne
  cB.wceq cD cP cR cF c.0
  hpcoe1nzex.d hpcoe1nzex.p hpcoe1nzex.z hpcoe1nzex.b
  deg1nn0cl
  cA.wceq cB.wceq cD cP cR cF cY c.0
  hpcoe1nzex.d hpcoe1nzex.p hpcoe1nzex.z hpcoe1nzex.b
  hpcoe1nzex.y hpcoe1nzex.a deg1ldg
  jca
  vn cv cA.wceq cfv cY wne
  cF cD cfv cA.wceq cfv cY wne
  vn cF cD cfv cn0
  vn cv cF cD cfv wceq
  vn cv cA.wceq cfv cF cD cfv cA.wceq cfv cY
  vn cv cF cD cfv wceq
  vn cv cF cD cfv cA.wceq
  vn cv cF cD cfv wceq
  id fveq2d neeq1d rspcev syl
$.
$}
