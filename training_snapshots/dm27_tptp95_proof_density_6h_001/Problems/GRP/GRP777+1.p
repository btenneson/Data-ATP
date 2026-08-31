%------------------------------------------------------------------------------
% File     : GRP777+1 : TPTP v9.3.1. Released v4.1.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Napoleon's quasigroups: the centroid relation
% Version  : Especial.
% English  :

% Refs     : [Sta09] Stanovsky (2009), Email to Geoff Sutcliffe
% Source   : [Sta09]
% Names    : napoleon1 [Sta09]

% Status   : Theorem
% Rating   : 0.00 v9.1.0, 0.12 v9.0.0, 0.10 v8.2.0, 0.17 v7.5.0, 0.19 v7.4.0, 0.24 v7.3.0, 0.23 v7.2.0, 0.25 v7.1.0, 0.27 v7.0.0, 0.07 v6.4.0, 0.21 v6.2.0, 0.18 v6.1.0, 0.25 v5.5.0, 0.12 v5.4.0, 0.22 v5.3.0, 0.00 v5.2.0, 0.67 v5.0.0, 0.00 v4.1.0
% Syntax   : Number of formulae    :   10 (  10 unt;   0 def)
%            Number of atoms       :   10 (  10 equ)
%            Maximal formula atoms :    1 (   1 avg)
%            Number of connectives :    0 (   0   ~;   0   |;   0   &)
%                                         (   0 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   3 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    7 (   7 usr;   3 con; 0-3 aty)
%            Number of variables   :   19 (  19   !;   0   ?)
% SPC      : FOF_THM_RFO_PEQ

% Comments :
%------------------------------------------------------------------------------
fof(sos01,axiom,
    ! [B,A] : difference(A,product(A,B)) = B ).

fof(sos02,axiom,
    ! [B,A] : product(A,difference(A,B)) = B ).

fof(sos03,axiom,
    ! [B,A] : quotient(product(A,B),B) = A ).

fof(sos04,axiom,
    ! [B,A] : product(quotient(A,B),B) = A ).

fof(sos05,axiom,
    ! [D,C,B,A] : product(product(A,B),product(C,D)) = product(product(A,C),product(B,D)) ).

fof(sos06,axiom,
    ! [A] : product(A,A) = A ).

%----Napoleon
fof(sos07,axiom,
    ! [B,A] : product(product(product(A,B),B),product(B,product(B,A))) = B ).

fof(sos08,axiom,
    ! [C,B,A] : bigC(A,B,C) = product(product(A,B),product(C,A)) ).

fof(sos09,axiom,
    product(product(a,c),product(c,b)) = product(a,b) ).

fof(goals,conjecture,
    ! [X0] : bigC(a,b,X0) = bigC(c,c,X0) ).

%------------------------------------------------------------------------------
