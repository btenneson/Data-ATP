%------------------------------------------------------------------------------
% File     : GRP774+1 : TPTP v9.3.1. Released v4.1.0.
% Domain   : Group Theory (Semigroups)
% Problem  : Green's relation D is a congruence
% Version  : Especial.
% English  :

% Refs     : [Sta09] Stanovsky (2009), Email to Geoff Sutcliffe
% Source   : [Sta09]
% Names    : green1 [Sta09]

% Status   : Theorem
% Rating   : 0.43 v9.3.0, 0.55 v9.0.0, 0.58 v8.1.0, 0.61 v7.5.0, 0.72 v7.4.0, 0.67 v7.3.0, 0.72 v7.1.0, 0.74 v7.0.0, 0.63 v6.4.0, 0.69 v6.3.0, 0.71 v6.2.0, 0.76 v6.1.0, 0.83 v6.0.0, 0.74 v5.5.0, 0.81 v5.4.0, 0.86 v5.3.0, 0.89 v5.2.0, 0.00 v4.1.0
% Syntax   : Number of formulae    :    4 (   2 unt;   0 def)
%            Number of atoms       :    8 (   4 equ)
%            Maximal formula atoms :    3 (   2 avg)
%            Number of connectives :    4 (   0   ~;   0   |;   2   &)
%                                         (   1 <=>;   1  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    7 (   5 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    2 (   1 usr;   0 prp; 2-2 aty)
%            Number of functors    :    1 (   1 usr;   0 con; 2-2 aty)
%            Number of variables   :   10 (  10   !;   0   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments :
%------------------------------------------------------------------------------
%----Semigroup
fof(sos01,axiom,
    ! [C,B,A] : product(product(A,B),C) = product(A,product(B,C)) ).

%----Idempotent
fof(sos02,axiom,
    ! [A] : product(A,A) = A ).

%----Green's relation D
fof(sos03,axiom,
    ! [X0,X1] :
      ( d(X0,X1)
    <=> ( product(X0,product(X1,X0)) = X0
        & product(X1,product(X0,X1)) = X1 ) ) ).

fof(goals,conjecture,
    ! [X2,X3,X4,X5] :
      ( ( d(X2,X3)
        & d(X4,X5) )
     => d(product(X2,X4),product(X3,X5)) ) ).

%------------------------------------------------------------------------------
