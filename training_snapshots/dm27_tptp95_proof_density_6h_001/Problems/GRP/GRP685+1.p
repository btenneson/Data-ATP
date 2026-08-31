%------------------------------------------------------------------------------
% File     : GRP685+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Axioms of rectangular loops - d
% Version  : Especial.
% English  :

% Refs     : [KP05]  Kinyon & Phillips (2005), Rectangular Quasigroups and
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : KP05 [PS08]

% Status   : Theorem
% Rating   : 0.12 v9.3.0, 0.00 v9.0.0, 0.05 v8.2.0, 0.17 v8.1.0, 0.13 v7.5.0, 0.19 v7.4.0, 0.24 v7.3.0, 0.08 v7.1.0, 0.09 v7.0.0, 0.13 v6.4.0, 0.21 v6.2.0, 0.27 v6.1.0, 0.25 v6.0.0, 0.33 v5.5.0, 0.12 v5.4.0, 0.22 v5.3.0, 0.00 v5.1.0, 0.14 v5.0.0, 0.25 v4.1.0, 0.27 v4.0.1, 0.50 v4.0.0
% Syntax   : Number of formulae    :    8 (   7 unt;   0 def)
%            Number of atoms       :    9 (   9 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   1   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   4 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    3 (   3 usr;   0 con; 2-2 aty)
%            Number of variables   :   19 (  19   !;   0   ?)
% SPC      : FOF_THM_RFO_PEQ

% Comments :
%------------------------------------------------------------------------------
fof(f01,axiom,
    ! [A] : ld(A,mult(A,A)) = A ).

fof(f02,axiom,
    ! [A] : rd(mult(A,A),A) = A ).

fof(f03,axiom,
    ! [B,A] : mult(A,ld(A,B)) = ld(A,mult(A,B)) ).

fof(f04,axiom,
    ! [B,A] : mult(rd(A,B),B) = rd(mult(A,B),B) ).

fof(f05,axiom,
    ! [D,C,B,A] : ld(ld(A,B),mult(ld(A,B),mult(C,D))) = mult(ld(A,mult(A,C)),D) ).

fof(f06,axiom,
    ! [D,C,B,A] : rd(mult(mult(A,B),rd(C,D)),rd(C,D)) = mult(A,rd(mult(B,D),D)) ).

fof(f07,axiom,
    ! [B,A] : ld(A,mult(A,ld(B,B))) = rd(mult(rd(A,A),B),B) ).

fof(goals,conjecture,
    ! [X6,X7,X8] :
      ( rd(mult(X6,ld(X7,X8)),ld(X7,X8)) = rd(mult(X6,X8),X8)
      & rd(mult(X6,rd(X7,X8)),rd(X7,X8)) = rd(mult(X6,X8),X8) ) ).

%------------------------------------------------------------------------------
