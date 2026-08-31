%------------------------------------------------------------------------------
% File     : GRP775+1 : TPTP v9.3.1. Released v4.1.0.
% Domain   : Group Theory (Semigroups)
% Problem  : Equivalent definition for Green's relation D
% Version  : Especial.
% English  :

% Refs     : [Sta09] Stanovsky (2009), Email to Geoff Sutcliffe
% Source   : [Sta09]
% Names    : green2 [Sta09]

% Status   : Theorem
% Rating   : 0.35 v9.3.0, 0.33 v9.1.0, 0.36 v9.0.0, 0.42 v8.2.0, 0.36 v8.1.0, 0.42 v7.5.0, 0.53 v7.4.0, 0.30 v7.3.0, 0.34 v7.1.0, 0.30 v7.0.0, 0.33 v6.4.0, 0.38 v6.2.0, 0.40 v6.1.0, 0.43 v6.0.0, 0.35 v5.5.0, 0.48 v5.4.0, 0.54 v5.3.0, 0.56 v5.2.0, 0.00 v4.1.0
% Syntax   : Number of formulae    :    6 (   2 unt;   0 def)
%            Number of atoms       :   14 (   8 equ)
%            Maximal formula atoms :    3 (   2 avg)
%            Number of connectives :    8 (   0   ~;   0   |;   4   &)
%                                         (   4 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    6 (   5 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    4 (   3 usr;   0 prp; 2-2 aty)
%            Number of functors    :    1 (   1 usr;   0 con; 2-2 aty)
%            Number of variables   :   13 (  12   !;   1   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments :
%------------------------------------------------------------------------------
%----Band
fof(sos01,axiom,
    ! [C,B,A] : product(product(A,B),C) = product(A,product(B,C)) ).

fof(sos02,axiom,
    ! [A] : product(A,A) = A ).

%----Green's relation L
fof(sos03,axiom,
    ! [X0,X1] :
      ( l(X0,X1)
    <=> ( product(X0,X1) = X0
        & product(X1,X0) = X1 ) ) ).

%----Green's relation R
fof(sos04,axiom,
    ! [X2,X3] :
      ( r(X2,X3)
    <=> ( product(X2,X3) = X3
        & product(X3,X2) = X2 ) ) ).

%----Green's relation D
fof(sos05,axiom,
    ! [X4,X5] :
      ( d(X4,X5)
    <=> ? [X6] :
          ( r(X4,X6)
          & l(X6,X5) ) ) ).

fof(goals,conjecture,
    ! [X7,X8] :
      ( d(X7,X8)
    <=> ( product(X7,product(X8,X7)) = X7
        & product(X8,product(X7,X8)) = X8 ) ) ).

%------------------------------------------------------------------------------
