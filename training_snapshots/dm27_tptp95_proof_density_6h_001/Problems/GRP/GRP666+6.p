%------------------------------------------------------------------------------
% File     : GRP666+6 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Inverse property A-loops are Moufang
% Version  : Especial.
% English  :

% Refs     : [KKP02] Kinyon et al. (2002), Every Diassociative A-loop is M
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : KKP02a [PS08]

% Status   : Theorem
% Rating   : 0.88 v9.3.0, 0.73 v9.1.0, 0.82 v9.0.0, 0.85 v8.2.0, 0.88 v8.1.0, 0.91 v7.5.0, 0.86 v7.4.0, 0.88 v7.3.0, 0.77 v7.2.0, 0.75 v7.1.0, 0.73 v7.0.0, 0.87 v6.4.0, 0.86 v6.3.0, 0.79 v6.2.0, 0.73 v6.1.0, 0.83 v5.5.0, 0.75 v5.4.0, 0.89 v5.3.0, 0.67 v5.2.0, 0.86 v5.0.0, 0.88 v4.1.0, 0.91 v4.0.1, 0.90 v4.0.0
% Syntax   : Number of formulae    :   12 (  11 unt;   0 def)
%            Number of atoms       :   15 (  15 equ)
%            Maximal formula atoms :    4 (   1 avg)
%            Number of connectives :    3 (   0   ~;   3   |;   0   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    7 (   4 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   1 con; 0-2 aty)
%            Number of variables   :   37 (  37   !;   0   ?)
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
    ! [D,C,B,A] : ld(mult(A,B),mult(A,mult(B,mult(C,D)))) = mult(ld(mult(A,B),mult(A,mult(B,C))),ld(mult(A,B),mult(A,mult(B,D)))) ).

fof(f08,axiom,
    ! [D,C,B,A] : rd(mult(mult(mult(A,B),C),D),mult(C,D)) = mult(rd(mult(mult(A,C),D),mult(C,D)),rd(mult(mult(B,C),D),mult(C,D))) ).

fof(f09,axiom,
    ! [C,B,A] : ld(A,mult(mult(B,C),A)) = mult(ld(A,mult(B,A)),ld(A,mult(C,A))) ).

fof(f10,axiom,
    ! [B,A] : mult(i(A),mult(A,B)) = B ).

fof(f11,axiom,
    ! [B,A] : mult(mult(A,B),i(B)) = A ).

fof(goals,conjecture,
    ( ! [X0,X1,X2] : mult(X2,mult(X0,mult(X2,X1))) = mult(mult(mult(X2,X0),X2),X1)
    | ! [X3,X4,X5] : mult(X3,mult(X5,mult(X4,X5))) = mult(mult(mult(X3,X5),X4),X5)
    | ! [X6,X7,X8] : mult(mult(X8,X6),mult(X7,X8)) = mult(mult(X8,mult(X6,X7)),X8)
    | ! [X9,X10,X11] : mult(mult(X11,X9),mult(X10,X11)) = mult(X11,mult(mult(X9,X10),X11)) ) ).

%------------------------------------------------------------------------------
