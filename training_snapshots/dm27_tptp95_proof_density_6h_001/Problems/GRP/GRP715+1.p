%------------------------------------------------------------------------------
% File     : GRP715+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Strongly right alternative rings 1
% Version  : Especial.
% English  : If a has a 2-sided inverse, then R(a^-1) = R(a)^-1 and
%            L(a)^-1 = R(a)L(a^-1)R(a^-1).

% Refs     : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : KKPxx [PS08]

% Status   : Theorem
% Rating   : 0.00 v8.2.0, 0.08 v8.1.0, 0.04 v7.5.0, 0.05 v7.4.0, 0.06 v7.3.0, 0.00 v7.0.0, 0.13 v6.4.0, 0.14 v6.3.0, 0.21 v6.2.0, 0.36 v6.1.0, 0.25 v6.0.0, 0.17 v5.5.0, 0.12 v5.4.0, 0.11 v5.3.0, 0.00 v5.1.0, 0.14 v5.0.0, 0.25 v4.1.0, 0.36 v4.0.1, 0.60 v4.0.0
% Syntax   : Number of formulae    :   12 (  11 unt;   0 def)
%            Number of atoms       :   13 (  13 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   1   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    4 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    7 (   7 usr;   4 con; 0-2 aty)
%            Number of variables   :   18 (  18   !;   0   ?)
% SPC      : FOF_THM_RFO_PEQ

% Comments :
%------------------------------------------------------------------------------
fof(f01,axiom,
    ! [C,B,A] : plus(plus(A,B),C) = plus(A,plus(B,C)) ).

fof(f02,axiom,
    ! [B,A] : plus(A,B) = plus(B,A) ).

fof(f03,axiom,
    ! [A] : plus(A,op_0) = A ).

fof(f04,axiom,
    ! [A] : plus(A,minus(A)) = op_0 ).

fof(f05,axiom,
    ! [C,B,A] : mult(A,plus(B,C)) = plus(mult(A,B),mult(A,C)) ).

fof(f06,axiom,
    ! [C,B,A] : mult(mult(mult(A,B),C),B) = mult(A,mult(mult(B,C),B)) ).

fof(f07,axiom,
    ! [B,A] : mult(A,mult(B,B)) = mult(mult(A,B),B) ).

fof(f08,axiom,
    ! [A] : mult(A,unit) = A ).

fof(f09,axiom,
    ! [A] : mult(unit,A) = A ).

fof(f10,axiom,
    mult(op_a,op_b) = unit ).

fof(f11,axiom,
    mult(op_b,op_a) = unit ).

fof(goals,conjecture,
    ! [X0] :
      ( mult(mult(X0,op_a),op_b) = X0
      & mult(mult(X0,op_b),op_a) = X0 ) ).

%------------------------------------------------------------------------------
