%------------------------------------------------------------------------------
% File     : GRP012+5 : TPTP v9.3.1. Released v3.1.0.
% Domain   : Group Theory
% Problem  : Inverse of products = Product of inverses
% Version  : Especial.
% English  : The inverse of products equals the product of the inverse,
%            in opposite order

% Refs     : [Shu04] Shults (2004), Email to G. Sutcliffe
% Source   : [Shu04]
% Names    :

% Status   : Theorem
% Rating   : 0.20 v9.1.0, 0.33 v9.0.0, 0.12 v8.2.0, 0.20 v8.1.0, 0.21 v7.5.0, 0.33 v7.4.0, 0.12 v7.3.0, 0.14 v7.2.0, 0.17 v7.1.0, 0.25 v7.0.0, 0.14 v6.4.0, 0.07 v6.3.0, 0.08 v6.2.0, 0.09 v6.1.0, 0.24 v6.0.0, 0.25 v5.5.0, 0.29 v5.4.0, 0.22 v5.3.0, 0.35 v5.2.0, 0.07 v5.0.0, 0.15 v4.1.0, 0.17 v4.0.1, 0.21 v4.0.0, 0.20 v3.7.0, 0.29 v3.5.0, 0.25 v3.4.0, 0.00 v3.1.0
% Syntax   : Number of formulae    :    1 (   0 unt;   0 def)
%            Number of atoms       :   16 (   0 equ)
%            Maximal formula atoms :   16 (  16 avg)
%            Number of connectives :   15 (   0   ~;   0   |;  11   &)
%                                         (   0 <=>;   4  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   15 (  15 avg)
%            Maximal term depth    :    2 (   1 avg)
%            Number of predicates  :    1 (   1 usr;   0 prp; 3-3 aty)
%            Number of functors    :    1 (   1 usr;   0 con; 1-1 aty)
%            Number of variables   :   24 (  23   !;   1   ?)
% SPC      : FOF_THM_RFO_NEQ

% Comments :
%------------------------------------------------------------------------------
fof(prove_distribution,conjecture,
    ! [E] :
      ( ( ! [X,Y] :
          ? [Z] : product(X,Y,Z)
        & ! [X,Y,Z,U,V,W] :
            ( ( product(X,Y,U)
              & product(Y,Z,V)
              & product(U,Z,W) )
           => product(X,V,W) )
        & ! [X,Y,Z,U,V,W] :
            ( ( product(X,Y,U)
              & product(Y,Z,V)
              & product(X,V,W) )
           => product(U,Z,W) )
        & ! [X] : product(X,E,X)
        & ! [X] : product(E,X,X)
        & ! [X] : product(X,inverse(X),E)
        & ! [X] : product(inverse(X),X,E) )
     => ! [U,V,W,X] :
          ( ( product(inverse(U),inverse(V),W)
            & product(V,U,X) )
         => product(inverse(W),inverse(X),E) ) ) ).

%------------------------------------------------------------------------------
