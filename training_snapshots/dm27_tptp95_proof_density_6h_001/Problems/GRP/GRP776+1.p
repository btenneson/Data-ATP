%------------------------------------------------------------------------------
% File     : GRP776+1 : TPTP v9.3.1. Released v4.1.0.
% Domain   : Group Theory
% Problem  : A homomorphic mapping between two groups 
% Version  : Especial.
% English  : A mapping between two groups that respects multiplication is a 
%            homomorphism.

% Refs     : [Sta09] Stanovsky (2009), Email to Geoff Sutcliffe
% Source   : [Sta09]
% Names    : grp_hom [Sta09]

% Status   : Theorem
% Rating   : 0.30 v9.3.0, 0.36 v8.2.0, 0.39 v8.1.0, 0.33 v7.5.0, 0.44 v7.4.0, 0.30 v7.3.0, 0.31 v7.2.0, 0.34 v7.1.0, 0.30 v7.0.0, 0.37 v6.4.0, 0.42 v6.2.0, 0.52 v6.1.0, 0.67 v6.0.0, 0.61 v5.5.0, 0.70 v5.4.0, 0.75 v5.3.0, 0.81 v5.2.0, 0.00 v4.1.0
% Syntax   : Number of formulae    :   19 (   3 unt;   0 def)
%            Number of atoms       :   42 (  13 equ)
%            Maximal formula atoms :    4 (   2 avg)
%            Number of connectives :   24 (   1   ~;   1   |;   7   &)
%                                         (   0 <=>;  15  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    7 (   4 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    3 (   2 usr;   0 prp; 1-2 aty)
%            Number of functors    :    7 (   7 usr;   2 con; 0-2 aty)
%            Number of variables   :   25 (  25   !;   0   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments :
%------------------------------------------------------------------------------
%----G is closed under *, inv, eh
fof(sos01,axiom,
    ! [B,A] :
      ( ( g(A)
        & g(B) )
     => g(product(A,B)) ) ).

fof(sos02,axiom,
    ! [A] :
      ( g(A)
     => g(inv(A)) ) ).

fof(sos03,axiom,
    g(eh) ).

%----G is a group
fof(sos04,axiom,
    ! [C,B,A] :
      ( ( g(A)
        & g(B)
        & g(C) )
     => product(product(A,B),C) = product(A,product(B,C)) ) ).

fof(sos05,axiom,
    ! [A] :
      ( g(A)
     => product(eh,A) = A ) ).

fof(sos06,axiom,
    ! [A] :
      ( g(A)
     => product(A,eh) = A ) ).

fof(sos07,axiom,
    ! [A] :
      ( g(A)
     => product(A,inv(A)) = eh ) ).

fof(sos08,axiom,
    ! [A] :
      ( g(A)
     => product(inv(A),A) = eh ) ).

%----H is closed under *, inv, eh
fof(sos09,axiom,
    ! [B,A] :
      ( ( h(A)
        & h(B) )
     => h(sum(A,B)) ) ).

fof(sos10,axiom,
    ! [B,A] :
      ( h(A)
     => h(opp(B)) ) ).

fof(sos11,axiom,
    h(eg) ).

%----H is a group
fof(sos12,axiom,
    ! [C,B,A] :
      ( ( h(A)
        & h(B)
        & h(C) )
     => sum(sum(A,B),C) = sum(A,sum(B,C)) ) ).

fof(sos13,axiom,
    ! [A] :
      ( h(A)
     => sum(eg,A) = A ) ).

fof(sos14,axiom,
    ! [A] :
      ( h(A)
     => sum(A,eg) = A ) ).

fof(sos15,axiom,
    ! [A] :
      ( h(A)
     => sum(A,opp(A)) = eg ) ).

fof(sos16,axiom,
    ! [A] :
      ( h(A)
     => sum(opp(A),A) = eg ) ).

%----f: G -> H
fof(sos17,axiom,
    ! [A] :
      ( g(A)
     => h(f(A)) ) ).

fof(sos18,axiom,
    ! [B,A] : f(product(A,B)) = sum(f(A),f(B)) ).

%----f is a homomorphism
fof(goals,conjecture,
    ! [X0] :
      ( f(eh) = eg
      & ( ~ g(X0)
        | f(inv(X0)) = opp(f(X0)) ) ) ).

%------------------------------------------------------------------------------
