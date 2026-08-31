%------------------------------------------------------------------------------
% File     : GRP780+1 : TPTP v9.3.1. Released v4.1.0.
% Domain   : Group Theory (Quasigroups)
% Problem  : Napoleon's quasigroups: Lamoen's theorem
% Version  : Especial.
% English  :

% Refs     : [Sta09] Stanovsky (2009), Email to Geoff Sutcliffe
% Source   : [Sta09]
% Names    : napoleon4 [Sta09]

% Status   : Theorem
% Rating   : 0.61 v9.3.0, 0.67 v9.0.0, 0.69 v8.2.0, 0.75 v8.1.0, 0.78 v7.5.0, 0.81 v7.4.0, 0.77 v7.3.0, 0.79 v7.1.0, 0.74 v7.0.0, 0.77 v6.4.0, 0.73 v6.3.0, 0.71 v6.2.0, 0.76 v6.1.0, 0.83 v5.5.0, 0.89 v5.4.0, 0.86 v5.3.0, 0.89 v5.2.0, 0.67 v4.1.0
% Syntax   : Number of formulae    :   13 (  12 unt;   0 def)
%            Number of atoms       :   14 (   9 equ)
%            Maximal formula atoms :    2 (   1 avg)
%            Number of connectives :    1 (   0   ~;   0   |;   0   &)
%                                         (   1 <=>;   0  =>;   0  <=;   0 <~>)
%            Maximal formula depth :    5 (   3 avg)
%            Maximal term depth    :    4 (   1 avg)
%            Number of predicates  :    2 (   1 usr;   0 prp; 2-3 aty)
%            Number of functors    :   13 (  13 usr;   9 con; 0-3 aty)
%            Number of variables   :   21 (  21   !;   0   ?)
% SPC      : FOF_THM_RFO_SEQ

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
    ! [X0,X1,X2] :
      ( d(X0,X1,X2)
    <=> product(X0,X1) = product(X1,X2) ) ).

fof(sos09,axiom,
    ! [C,B,A] : bigC(A,B,C) = product(product(A,B),product(C,A)) ).

fof(sos10,axiom,
    d(a1,a2,a3) ).

fof(sos11,axiom,
    d(b1,b2,b3) ).

fof(sos12,axiom,
    d(c1,c2,c3) ).

fof(goals,conjecture,
    d(bigC(a1,b3,c2),bigC(a2,b1,c3),bigC(a3,b2,c1)) ).

%------------------------------------------------------------------------------
