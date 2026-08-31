%------------------------------------------------------------------------------
% File     : GRP667+6 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : 2-divisible ARIF loops are Moufang
% Version  : Especial.
% English  :

% Refs     : [KKP02] Kinyon et al. (2002), A Generalization of Moufang and
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : KKP02b [PS08]

% Status   : Theorem
% Rating   : 0.25 v9.3.0, 0.00 v9.1.0, 0.24 v9.0.0, 0.25 v8.2.0, 0.33 v8.1.0, 0.43 v7.4.0, 0.47 v7.3.0, 0.38 v7.2.0, 0.42 v7.1.0, 0.45 v7.0.0, 0.47 v6.4.0, 0.50 v6.3.0, 0.43 v6.2.0, 0.36 v6.1.0, 0.50 v5.5.0, 0.25 v5.4.0, 0.33 v5.3.0, 0.17 v5.2.0, 0.14 v5.1.0, 0.29 v5.0.0, 0.38 v4.1.0, 0.55 v4.0.1, 0.80 v4.0.0
% Syntax   : Number of formulae    :   10 (   9 unt;   0 def)
%            Number of atoms       :   13 (  13 equ)
%            Maximal formula atoms :    4 (   1 avg)
%            Number of connectives :    3 (   0   ~;   3   |;   0   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    7 (   3 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   1 con; 0-2 aty)
%            Number of variables   :   28 (  28   !;   0   ?)
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
    ! [C,B,A] : mult(mult(A,B),mult(mult(C,B),C)) = mult(mult(A,mult(mult(B,C),B)),C) ).

fof(f08,axiom,
    ! [B,A] : mult(mult(A,B),A) = mult(A,mult(B,A)) ).

fof(f09,axiom,
    ! [A] : mult(f(A),f(A)) = A ).

fof(goals,conjecture,
    ( ! [X0,X1,X2] : mult(X2,mult(X0,mult(X2,X1))) = mult(mult(mult(X2,X0),X2),X1)
    | ! [X3,X4,X5] : mult(X3,mult(X5,mult(X4,X5))) = mult(mult(mult(X3,X5),X4),X5)
    | ! [X6,X7,X8] : mult(mult(X8,X6),mult(X7,X8)) = mult(mult(X8,mult(X6,X7)),X8)
    | ! [X9,X10,X11] : mult(mult(X11,X9),mult(X10,X11)) = mult(X11,mult(mult(X9,X10),X11)) ) ).

%------------------------------------------------------------------------------
