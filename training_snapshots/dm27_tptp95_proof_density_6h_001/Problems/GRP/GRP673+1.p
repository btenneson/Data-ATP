%------------------------------------------------------------------------------
% File     : GRP673+1 : TPTP v9.3.1. Released v4.0.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Extra loop commutation property 2
% Version  : Especial.
% English  : In an extra loop, z commutes with [x;y; t] if and only if t
%            commutes with [x;y; z] if and only if [x;y; z][x;y; t] =
%            [x;y; zt].

% Refs     : [KK04]  Kinyon & Kunen (2004), The Structure of Extra Loops
%          : [PS08]  Phillips & Stanovsky (2008), Automated Theorem Proving
%          : [Sta08] Stanovsky (2008), Email to G. Sutcliffe
% Source   : [Sta08]
% Names    : KK04 [PS08]

% Status   : Theorem
% Rating   : 1.00 v4.0.0
% Syntax   : Number of formulae    :   10 (   9 unt;   0 def)
%            Number of atoms       :   11 (  11 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   1   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    4 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    9 (   9 usr;   5 con; 0-3 aty)
%            Number of variables   :   16 (  16   !;   0   ?)
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
    ! [C,B,A] : mult(A,mult(B,mult(C,A))) = mult(mult(mult(A,B),C),A) ).

fof(f08,axiom,
    ! [C,B,A] : asoc(A,B,C) = ld(mult(A,mult(B,C)),mult(mult(A,B),C)) ).

fof(f09,axiom,
    mult(op_t,asoc(op_x,op_y,op_z)) = mult(asoc(op_x,op_y,op_z),op_t) ).

fof(goals,conjecture,
    ( mult(op_z,asoc(op_x,op_y,op_t)) = mult(asoc(op_x,op_y,op_t),op_z)
    & mult(asoc(op_x,op_y,op_z),asoc(op_x,op_y,op_t)) = asoc(op_x,op_y,mult(op_z,op_t)) ) ).

%------------------------------------------------------------------------------
