%------------------------------------------------------------------------------
% File     : GRP660+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Bol-Moufang identity 3 implies a unit element
% Version  : Especial.
% English  :

% Refs     : [Kun96] Kunen (1996), Quasigroups, Loops, and Associative Law
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : Kun96b [PS08]

% Status   : Theorem
% Rating   : 0.25 v9.3.0, 0.00 v9.0.0, 0.10 v8.2.0, 0.21 v8.1.0, 0.17 v7.5.0, 0.19 v7.4.0, 0.24 v7.3.0, 0.08 v7.1.0, 0.09 v7.0.0, 0.13 v6.4.0, 0.21 v6.2.0, 0.27 v6.1.0, 0.25 v6.0.0, 0.33 v5.5.0, 0.12 v5.4.0, 0.22 v5.3.0, 0.00 v5.1.0, 0.14 v5.0.0, 0.25 v4.1.0, 0.36 v4.0.1, 0.70 v4.0.0
% Syntax   : Number of formulae    :    6 (   5 unt;   0 def)
%            Number of atoms       :    7 (   7 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   1   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    4 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    3 (   3 usr;   0 con; 2-2 aty)
%            Number of variables   :   13 (  12   !;   1   ?)
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
    ! [C,B,A] : mult(mult(mult(A,B),C),A) = mult(A,mult(B,mult(C,A))) ).

fof(goals,conjecture,
    ? [X0] :
    ! [X1] :
      ( mult(X1,X0) = X1
      & mult(X0,X1) = X1 ) ).

%------------------------------------------------------------------------------
