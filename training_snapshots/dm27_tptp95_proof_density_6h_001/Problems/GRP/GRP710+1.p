%------------------------------------------------------------------------------
% File     : GRP710+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : A magma with 2-sided inverses satisfying the C-law is a loop - 1a
% Version  : Especial.
% English  : In a Bol loop, if c is a commutant element, then c^2 is in the
%            left nucleus if and only if c is in the right nucleus.

% Refs     : [PV08]  Phillips & Vojtechovsky (2008), A Scoop from Groups: N
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : PV08 [PS08]

% Status   : Theorem
% Rating   : 0.12 v9.3.0, 0.00 v9.0.0, 0.05 v8.2.0, 0.17 v8.1.0, 0.13 v7.5.0, 0.19 v7.4.0, 0.24 v7.3.0, 0.08 v7.1.0, 0.09 v7.0.0, 0.13 v6.4.0, 0.21 v6.2.0, 0.27 v6.1.0, 0.25 v6.0.0, 0.33 v5.5.0, 0.12 v5.4.0, 0.22 v5.3.0, 0.00 v5.1.0, 0.14 v5.0.0, 0.25 v4.1.0, 0.27 v4.0.1, 0.50 v4.0.0
% Syntax   : Number of formulae    :    6 (   5 unt;   0 def)
%            Number of atoms       :    7 (   7 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   1   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    3 (   3 usr;   1 con; 0-2 aty)
%            Number of variables   :   13 (  11   !;   2   ?)
% SPC      : FOF_THM_RFO_PEQ

% Comments :
%------------------------------------------------------------------------------
fof(f01,axiom,
    ! [A] : mult(A,unit) = A ).

fof(f02,axiom,
    ! [A] : mult(unit,A) = A ).

fof(f03,axiom,
    ! [C,B,A] : mult(A,mult(B,mult(B,C))) = mult(mult(mult(A,B),B),C) ).

fof(f04,axiom,
    ! [A] : mult(A,i(A)) = unit ).

fof(f05,axiom,
    ! [A] : mult(i(A),A) = unit ).

fof(goals,conjecture,
    ( ! [X0,X1] :
      ? [X2] : mult(X0,X2) = X1
    & ! [X3,X4] :
      ? [X5] : mult(X5,X4) = X3 ) ).

%------------------------------------------------------------------------------
