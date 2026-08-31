%--------------------------------------------------------------------------
% File     : GRP194+1 : TPTP v9.3.1. Released v2.0.0.
% Domain   : Group Theory (Semigroups)
% Problem  : In semigroups, a surjective homomorphism maps the zero
% Version  : [Gol93] axioms.
% English  : If (F,*) and (H,+) are two semigroups, phi is a surjective
%            homomorphism from F to H, and id is a left zero for F,
%            then phi(id) is a left zero for H.

% Refs     : [Gol93] Goller (1993), Anwendung des Theorembeweisers SETHEO a
% Source   : [Gol93]
% Names    :

% Status   : Theorem
% Rating   : 0.26 v9.3.0, 0.15 v9.1.0, 0.18 v9.0.0, 0.19 v8.1.0, 0.22 v7.5.0, 0.25 v7.4.0, 0.10 v7.3.0, 0.14 v7.2.0, 0.10 v7.1.0, 0.13 v7.0.0, 0.20 v6.4.0, 0.23 v6.3.0, 0.21 v6.2.0, 0.36 v6.1.0, 0.47 v6.0.0, 0.35 v5.5.0, 0.37 v5.4.0, 0.50 v5.3.0, 0.48 v5.2.0, 0.40 v5.1.0, 0.33 v4.1.0, 0.35 v4.0.1, 0.30 v4.0.0, 0.29 v3.7.0, 0.15 v3.5.0, 0.16 v3.4.0, 0.21 v3.3.0, 0.14 v3.2.0, 0.18 v3.1.0, 0.11 v2.7.0, 0.17 v2.6.0, 0.14 v2.5.0, 0.12 v2.4.0, 0.25 v2.3.0, 0.33 v2.2.1, 0.00 v2.1.0
% Syntax   : Number of formulae    :    8 (   2 unt;   0 def)
%            Number of atoms       :   21 (   4 equ)
%            Maximal formula atoms :    4 (   2 avg)
%            Number of connectives :   13 (   0   ~;   0   |;   6   &)
%                                         (   1 <=>;   6  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    8 (   5 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    3 (   2 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   3 con; 0-3 aty)
%            Number of variables   :   15 (  14   !;   1   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments :
%--------------------------------------------------------------------------
%----Include Semigroup axioms
include('Axioms/GRP007+0.ax').
%--------------------------------------------------------------------------
%----Definition of a homomorphism
fof(homomorphism1,axiom,
    ! [X] :
      ( group_member(X,f)
     => group_member(phi(X),h) ) ).

fof(homomorphism2,axiom,
    ! [X,Y] :
      ( ( group_member(X,f)
        & group_member(Y,f) )
     => multiply(h,phi(X),phi(Y)) = phi(multiply(f,X,Y)) ) ).

fof(surjective,axiom,
    ! [X] :
      ( group_member(X,h)
     => ? [Y] :
          ( group_member(Y,f)
          & phi(Y) = X ) ) ).

%----Definition of left zero
fof(left_zero,axiom,
    ! [G,X] :
      ( left_zero(G,X)
    <=> ( group_member(X,G)
        & ! [Y] :
            ( group_member(Y,G)
           => multiply(G,X,Y) = X ) ) ) ).

%----The conjecture
fof(left_zero_for_f,hypothesis,
    left_zero(f,f_left_zero) ).

fof(prove_left_zero_h,conjecture,
    left_zero(h,phi(f_left_zero)) ).

%--------------------------------------------------------------------------
