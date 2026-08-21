$(
  HaloProof order/halo development extension.

  This file is concatenated AFTER the exact frozen set.mm snapshot by the
  HaloProof campaign.  It introduces no new axiom.  The first milestone is to
  instantiate native set.mm machinery at the concrete benchmark field

      P = Poly1(RRfld)
      H = Frac(P).

  The four theorems below have been independently stack-checked against the
  frozen set(3).mm snapshot with SHA-256

      1016D7EDB0508ABDE0FE240BB5243E588C5067F8CB10EE6E1CC5733FC05ACDB5

  They are intentionally small.  Later milestones should be added only after
  the Metamath verifier accepts them.

  Remaining theorem families, in order:

  ES1  define least-nonzero-coefficient sign for nonzero Poly1(RRfld)
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
