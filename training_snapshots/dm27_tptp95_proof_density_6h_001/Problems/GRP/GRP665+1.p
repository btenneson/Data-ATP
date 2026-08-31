%------------------------------------------------------------------------------
% File     : GRP665+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Conjugacy closed implies commutant in the nucleus
% Version  : Especial.
% English  :

% Refs     : [Kun00] Kunen (2000), The Structure of Conjugacy Closed Loops
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : Kun00 [PS08]

% Status   : Theorem
% Rating   : 0.12 v9.3.0, 0.18 v9.1.0, 0.12 v9.0.0, 0.10 v8.2.0, 0.08 v8.1.0, 0.09 v7.5.0, 0.10 v7.4.0, 0.12 v7.3.0, 0.15 v7.2.0, 0.17 v7.1.0, 0.18 v7.0.0, 0.13 v6.4.0, 0.14 v6.2.0, 0.18 v6.1.0, 0.17 v6.0.0, 0.25 v5.5.0, 0.38 v5.4.0, 0.22 v5.3.0, 0.17 v5.2.0, 0.14 v5.1.0, 0.29 v5.0.0, 0.38 v4.1.0, 0.27 v4.0.1, 0.60 v4.0.0
% Syntax   : Number of formulae    :   10 (   9 unt;   0 def)
%            Number of atoms       :   12 (  12 equ)
%            Maximal formula atoms :    3 (   1 avg)
%            Number of connectives :    2 (   0   ~;   0   |;   2   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   2 con; 0-2 aty)
%            Number of variables   :   19 (  19   !;   0   ?)
% SPC      : FOF_THM_RFO_PEQ

% Comments :
%------------------------------------------------------------------------------
fof(f01,axiom,
    ! [B,A] : mult(A,ld(A,B)) = B ).

fof(f02,axiom,
    ! [B,A] : ld(A,mult(A,B)) = B ).

fof(f03,axiom,
    ! [B,A] : mult(rd(A,B),B) = A ).

fof(f04,axiom,
    ! [B,A] : rd(mult(A,B),B) = A ).

fof(f05,axiom,
    ! [A] : mult(A,unit) = A ).

fof(f06,axiom,
    ! [A] : mult(unit,A) = A ).

fof(f07,axiom,
    ! [C,B,A] : mult(A,mult(B,C)) = mult(rd(mult(A,B),A),mult(A,C)) ).

fof(f08,axiom,
    ! [C,B,A] : mult(mult(A,B),C) = mult(mult(A,C),ld(C,mult(B,C))) ).

fof(f09,axiom,
    ! [A] : mult(op_c,A) = mult(A,op_c) ).

fof(goals,conjecture,
    ! [X0,X1] :
      ( mult(op_c,mult(X0,X1)) = mult(mult(op_c,X0),X1)
      & mult(mult(X0,op_c),X1) = mult(X0,mult(op_c,X1))
      & mult(mult(X0,X1),op_c) = mult(X0,mult(X1,op_c)) ) ).

%------------------------------------------------------------------------------
