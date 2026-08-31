%------------------------------------------------------------------------------
% File     : GRP667+1 : TPTP v9.3.1. Released v4.0.0.
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
% Rating   : 0.25 v9.3.0, 0.00 v9.1.0, 0.18 v9.0.0, 0.20 v8.2.0, 0.38 v8.1.0, 0.43 v7.5.0, 0.33 v7.4.0, 0.41 v7.3.0, 0.38 v7.2.0, 0.33 v7.1.0, 0.36 v7.0.0, 0.27 v6.4.0, 0.36 v6.3.0, 0.29 v6.2.0, 0.27 v6.1.0, 0.42 v6.0.0, 0.50 v5.5.0, 0.38 v5.4.0, 0.44 v5.3.0, 0.17 v5.2.0, 0.14 v5.1.0, 0.29 v5.0.0, 0.38 v4.1.0, 0.45 v4.0.1, 0.70 v4.0.0
% Syntax   : Number of formulae    :   13 (  10 unt;   0 def)
%            Number of atoms       :   16 (  16 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    3 (   0   ~;   0   |;   0   &)
%                                         (   0 <=>;   3  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   3 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    8 (   8 usr;   4 con; 0-2 aty)
%            Number of variables   :   25 (  25   !;   0   ?)
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

fof(f10,axiom,
    ! [X0,X1,X2] :
      ( mult(X0,mult(X1,mult(X2,X1))) = mult(mult(mult(X0,X1),X2),X1)
     => mult(X1,mult(X0,mult(X1,X2))) = mult(mult(mult(X1,X0),X1),X2) ) ).

fof(f11,axiom,
    ! [X3,X4,X5] :
      ( mult(mult(X3,X4),mult(X5,X3)) = mult(mult(X3,mult(X4,X5)),X3)
     => mult(X3,mult(X4,mult(X3,X5))) = mult(mult(mult(X3,X4),X3),X5) ) ).

fof(f12,axiom,
    ! [X6,X7,X8] :
      ( mult(mult(X6,X7),mult(X8,X6)) = mult(X6,mult(mult(X7,X8),X6))
     => mult(X6,mult(X7,mult(X6,X8))) = mult(mult(mult(X6,X7),X6),X8) ) ).

fof(goals,conjecture,
    mult(a,mult(b,mult(a,c))) = mult(mult(mult(a,b),a),c) ).

%------------------------------------------------------------------------------
