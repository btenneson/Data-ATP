%------------------------------------------------------------------------------
% File     : GRP702+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : In C-loops the nucleus is normal - a
% Version  : Especial.
% English  :

% Refs     : [PV06]  Phillips & Vojtechovsky (2006), C-loops: an Introducti
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : PV06 [PS08]

% Status   : Theorem
% Rating   : 0.00 v8.2.0, 0.04 v7.5.0, 0.05 v7.4.0, 0.06 v7.3.0, 0.00 v6.4.0, 0.07 v6.2.0, 0.00 v5.1.0, 0.14 v5.0.0, 0.25 v4.1.0, 0.27 v4.0.1, 0.40 v4.0.0
% Syntax   : Number of formulae    :   14 (  13 unt;   0 def)
%            Number of atoms       :   16 (  16 equ)
%            Maximal formula atoms :    3 (   1 avg)
%            Number of connectives :    2 (   0   ~;   0   |;   2   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   3 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    8 (   8 usr;   5 con; 0-2 aty)
%            Number of variables   :   26 (  26   !;   0   ?)
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
    ! [C,B,A] : mult(A,mult(B,mult(B,C))) = mult(mult(mult(A,B),B),C) ).

fof(f08,axiom,
    ! [B,A] : mult(op_c,mult(A,B)) = mult(mult(op_c,A),B) ).

fof(f09,axiom,
    ! [B,A] : mult(A,mult(B,op_c)) = mult(mult(A,B),op_c) ).

fof(f10,axiom,
    ! [B,A] : mult(A,mult(op_c,B)) = mult(mult(A,op_c),B) ).

fof(f11,axiom,
    ! [A] : op_d = ld(A,mult(op_c,A)) ).

fof(f12,axiom,
    ! [B,A] : op_e = mult(mult(rd(op_c,mult(A,B)),B),A) ).

fof(f13,axiom,
    ! [B,A] : op_f = mult(A,mult(B,ld(mult(A,B),op_c))) ).

fof(goals,conjecture,
    ! [X0,X1] :
      ( mult(op_d,mult(X0,X1)) = mult(mult(op_d,X0),X1)
      & mult(X0,mult(X1,op_d)) = mult(mult(X0,X1),op_d)
      & mult(X0,mult(op_d,X1)) = mult(mult(X0,op_d),X1) ) ).

%------------------------------------------------------------------------------
