%------------------------------------------------------------------------------
% File     : GRP700+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Variety of power associative, WIP conjugacy closed loops - 2c
% Version  : Especial.
% English  :

% Refs     : [Phi06] Phillips (2006), A Short Basis for the Variety of WIP
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : Phi06 [PS08]

% Status   : Theorem
% Rating   : 0.00 v8.2.0, 0.08 v8.1.0, 0.09 v7.5.0, 0.10 v7.4.0, 0.12 v7.3.0, 0.00 v6.4.0, 0.07 v6.2.0, 0.18 v6.1.0, 0.17 v5.5.0, 0.12 v5.4.0, 0.22 v5.3.0, 0.00 v5.1.0, 0.14 v5.0.0, 0.25 v4.1.0, 0.18 v4.0.1, 0.60 v4.0.0
% Syntax   : Number of formulae    :    9 (   8 unt;   0 def)
%            Number of atoms       :   10 (  10 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   1   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    4 (   3 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    4 (   4 usr;   1 con; 0-2 aty)
%            Number of variables   :   18 (  17   !;   1   ?)
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
    ! [C,B,A] : mult(mult(mult(A,B),A),mult(A,C)) = mult(A,mult(mult(mult(B,A),A),C)) ).

fof(f08,axiom,
    ! [C,B,A] : mult(mult(A,B),mult(B,mult(C,B))) = mult(mult(A,mult(B,mult(B,C))),B) ).

fof(goals,conjecture,
    ! [X0] :
    ? [X1] :
      ( mult(X1,X0) = unit
      & mult(X0,X1) = unit ) ).

%------------------------------------------------------------------------------
