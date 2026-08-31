%------------------------------------------------------------------------------
% File     : GRP748+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Right alternative loop rings: a lemma
% Version  : Especial.
% English  :

% Refs     : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : CGKxx_4 [Sta08]

% Status   : Theorem
% Rating   : 0.38 v9.3.0, 0.09 v9.1.0, 0.06 v9.0.0, 0.10 v8.2.0, 0.25 v8.1.0, 0.22 v7.5.0, 0.24 v7.4.0, 0.29 v7.3.0, 0.08 v7.2.0, 0.00 v7.0.0, 0.13 v6.4.0, 0.21 v6.2.0, 0.18 v6.1.0, 0.17 v6.0.0, 0.25 v5.5.0, 0.12 v5.4.0, 0.22 v5.3.0, 0.00 v4.1.0, 0.18 v4.0.1, 0.30 v4.0.0
% Syntax   : Number of formulae    :   12 (  10 unt;   0 def)
%            Number of atoms       :   16 (  16 equ)
%            Maximal formula atoms :    4 (   1 avg)
%            Number of connectives :    4 (   0   ~;   4   |;   0   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    7 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   1 con; 0-2 aty)
%            Number of variables   :   31 (  31   !;   0   ?)
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
    ! [C,B,A] : mult(mult(mult(A,B),C),B) = mult(A,mult(mult(B,C),B)) ).

fof(f08,axiom,
    ! [B,A] : mult(mult(A,B),i(B)) = A ).

fof(f09,axiom,
    ! [A] : mult(A,i(A)) = unit ).

fof(f10,axiom,
    ! [A] : mult(i(A),A) = unit ).

fof(f11,axiom,
    ! [B,A] :
      ( mult(A,B) = mult(B,A)
      | mult(i(A),mult(A,B)) = B ) ).

fof(goals,conjecture,
    ( ! [X0,X1,X2] : mult(X2,mult(X0,mult(X2,X1))) = mult(mult(mult(X2,X0),X2),X1)
    | ! [X3,X4,X5] : mult(X3,mult(X5,mult(X4,X5))) = mult(mult(mult(X3,X5),X4),X5)
    | ! [X6,X7,X8] : mult(mult(X8,X6),mult(X7,X8)) = mult(mult(X8,mult(X6,X7)),X8)
    | ! [X9,X10,X11] : mult(mult(X11,X9),mult(X10,X11)) = mult(X11,mult(mult(X9,X10),X11)) ) ).

%------------------------------------------------------------------------------
