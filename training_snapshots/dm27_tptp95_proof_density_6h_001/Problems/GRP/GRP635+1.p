%------------------------------------------------------------------------------
% File     : GRP635+1 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Lattice of Subgroups of a Group T06
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Gan96] Ganczarski (1996), On the Lattice of Subgroups of a Gr
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t6_latsubgr [Urb08]

% Status   : Theorem
% Rating   : 0.96 v9.3.0, 1.00 v3.4.0
% Syntax   : Number of formulae    :   71 (  20 unt;   0 def)
%            Number of atoms       :  278 (  25 equ)
%            Maximal formula atoms :   17 (   3 avg)
%            Number of connectives :  252 (  45   ~;   2   |; 116   &)
%                                         (   8 <=>;  81  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   14 (   6 avg)
%            Maximal term depth    :    4 (   1 avg)
%            Number of predicates  :   21 (  19 usr;   1 prp; 0-3 aty)
%            Number of functors    :   15 (  15 usr;   1 con; 0-4 aty)
%            Number of variables   :  160 ( 143   !;  17   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Normal version: includes the axioms (which may be theorems from
%            other articles) and background that are possibly necessary.
%          : Translated by MPTP from the Mizar Mathematical Library 4.48.930.
%          : The problem encoding is based on set theory.
%------------------------------------------------------------------------------
fof(t6_latsubgr,conjecture,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( ~ v3_struct_0(B)
            & v3_group_1(B)
            & v4_group_1(B)
            & l1_group_1(B) )
         => ! [C] :
              ( ( v1_funct_1(C)
                & v1_funct_2(C,u1_struct_0(A),u1_struct_0(B))
                & v1_group_6(C,A,B)
                & m2_relset_1(C,u1_struct_0(A),u1_struct_0(B)) )
             => ! [D] :
                  ( m1_group_2(D,A)
                 => ? [E] :
                      ( v1_group_1(E)
                      & m1_group_2(E,B)
                      & u1_struct_0(E) = k2_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(D)) ) ) ) ) ) ).

fof(abstractness_v1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => ( v1_group_1(A)
       => A = g1_group_1(u1_struct_0(A),u1_group_1(A)) ) ) ).

fof(antisymmetry_r2_hidden,axiom,
    ! [A,B] :
      ( r2_hidden(A,B)
     => ~ r2_hidden(B,A) ) ).

fof(cc1_funct_2,axiom,
    ! [A,B,C] :
      ( m1_relset_1(C,A,B)
     => ( ( v1_funct_1(C)
          & v1_partfun1(C,A,B) )
       => ( v1_funct_1(C)
          & v1_funct_2(C,A,B) ) ) ) ).

fof(cc1_relset_1,axiom,
    ! [A,B,C] :
      ( m1_subset_1(C,k1_zfmisc_1(k2_zfmisc_1(A,B)))
     => v1_relat_1(C) ) ).

fof(cc5_funct_2,axiom,
    ! [A,B] :
      ( ~ v1_xboole_0(B)
     => ! [C] :
          ( m1_relset_1(C,A,B)
         => ( ( v1_funct_1(C)
              & v1_funct_2(C,A,B) )
           => ( v1_funct_1(C)
              & v1_partfun1(C,A,B)
              & v1_funct_2(C,A,B) ) ) ) ) ).

fof(cc6_funct_2,axiom,
    ! [A,B] :
      ( ( ~ v1_xboole_0(A)
        & ~ v1_xboole_0(B) )
     => ! [C] :
          ( m1_relset_1(C,A,B)
         => ( ( v1_funct_1(C)
              & v1_funct_2(C,A,B) )
           => ( v1_funct_1(C)
              & ~ v1_xboole_0(C)
              & v1_partfun1(C,A,B)
              & v1_funct_2(C,A,B) ) ) ) ) ).

fof(d12_funct_1,axiom,
    ! [A] :
      ( ( v1_relat_1(A)
        & v1_funct_1(A) )
     => ! [B,C] :
          ( C = k9_relat_1(A,B)
        <=> ! [D] :
              ( r2_hidden(D,C)
            <=> ? [E] :
                  ( r2_hidden(E,k1_relat_1(A))
                  & r2_hidden(E,B)
                  & D = k1_funct_1(A,E) ) ) ) ) ).

fof(d1_funct_2,axiom,
    ! [A,B,C] :
      ( m2_relset_1(C,A,B)
     => ( ( ( B = k1_xboole_0
           => A = k1_xboole_0 )
         => ( v1_funct_2(C,A,B)
          <=> A = k4_relset_1(A,B,C) ) )
        & ( B = k1_xboole_0
         => ( A = k1_xboole_0
            | ( v1_funct_2(C,A,B)
            <=> C = k1_xboole_0 ) ) ) ) ) ).

fof(d1_rlvect_1,axiom,
    ! [A] :
      ( l1_struct_0(A)
     => ! [B] :
          ( r1_rlvect_1(A,B)
        <=> r2_hidden(B,u1_struct_0(A)) ) ) ).

fof(d7_group_6,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( ~ v3_struct_0(B)
            & l1_group_1(B) )
         => ! [C] :
              ( ( v1_funct_1(C)
                & v1_funct_2(C,u1_struct_0(A),u1_struct_0(B))
                & m2_relset_1(C,u1_struct_0(A),u1_struct_0(B)) )
             => ( v1_group_6(C,A,B)
              <=> ! [D] :
                    ( m1_subset_1(D,u1_struct_0(A))
                   => ! [E] :
                        ( m1_subset_1(E,u1_struct_0(A))
                       => k8_funct_2(u1_struct_0(A),u1_struct_0(B),C,k1_group_1(A,D,E)) = k1_group_1(B,k8_funct_2(u1_struct_0(A),u1_struct_0(B),C,D),k8_funct_2(u1_struct_0(A),u1_struct_0(B),C,E)) ) ) ) ) ) ) ).

fof(dt_g1_group_1,axiom,
    ! [A,B] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ( v1_group_1(g1_group_1(A,B))
        & l1_group_1(g1_group_1(A,B)) ) ) ).

fof(dt_k1_funct_1,axiom,
    $true ).

fof(dt_k1_group_1,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & l1_group_1(A)
        & m1_subset_1(B,u1_struct_0(A))
        & m1_subset_1(C,u1_struct_0(A)) )
     => m1_subset_1(k1_group_1(A,B,C),u1_struct_0(A)) ) ).

fof(dt_k1_relat_1,axiom,
    $true ).

fof(dt_k1_xboole_0,axiom,
    $true ).

fof(dt_k1_zfmisc_1,axiom,
    $true ).

fof(dt_k2_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( v1_funct_1(C)
        & v1_funct_2(C,A,B)
        & m1_relset_1(C,A,B) )
     => m1_subset_1(k2_funct_2(A,B,C,D),k1_zfmisc_1(B)) ) ).

fof(dt_k2_group_1,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l1_group_1(A) )
     => m1_subset_1(k2_group_1(A),u1_struct_0(A)) ) ).

fof(dt_k2_zfmisc_1,axiom,
    $true ).

fof(dt_k3_group_1,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_subset_1(B,u1_struct_0(A)) )
     => m1_subset_1(k3_group_1(A,B),u1_struct_0(A)) ) ).

fof(dt_k4_relset_1,axiom,
    ! [A,B,C] :
      ( m1_relset_1(C,A,B)
     => m1_subset_1(k4_relset_1(A,B,C),k1_zfmisc_1(A)) ) ).

fof(dt_k8_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( ~ v1_xboole_0(A)
        & v1_funct_1(C)
        & v1_funct_2(C,A,B)
        & m1_relset_1(C,A,B)
        & m1_subset_1(D,A) )
     => m1_subset_1(k8_funct_2(A,B,C,D),B) ) ).

fof(dt_k9_relat_1,axiom,
    $true ).

fof(dt_l1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => l1_struct_0(A) ) ).

fof(dt_l1_struct_0,axiom,
    $true ).

fof(dt_m1_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ( ~ v3_struct_0(B)
            & v3_group_1(B)
            & l1_group_1(B) ) ) ) ).

fof(dt_m1_relset_1,axiom,
    $true ).

fof(dt_m1_subset_1,axiom,
    $true ).

fof(dt_m2_relset_1,axiom,
    ! [A,B,C] :
      ( m2_relset_1(C,A,B)
     => m1_subset_1(C,k1_zfmisc_1(k2_zfmisc_1(A,B))) ) ).

fof(dt_u1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => ( v1_funct_1(u1_group_1(A))
        & v1_funct_2(u1_group_1(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A))
        & m2_relset_1(u1_group_1(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A)) ) ) ).

fof(dt_u1_struct_0,axiom,
    $true ).

fof(existence_l1_group_1,axiom,
    ? [A] : l1_group_1(A) ).

fof(existence_l1_struct_0,axiom,
    ? [A] : l1_struct_0(A) ).

fof(existence_m1_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & l1_group_1(A) )
     => ? [B] : m1_group_2(B,A) ) ).

fof(existence_m1_relset_1,axiom,
    ! [A,B] :
    ? [C] : m1_relset_1(C,A,B) ).

fof(existence_m1_subset_1,axiom,
    ! [A] :
    ? [B] : m1_subset_1(B,A) ).

fof(existence_m2_relset_1,axiom,
    ! [A,B] :
    ? [C] : m2_relset_1(C,A,B) ).

fof(fc1_struct_0,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l1_struct_0(A) )
     => ~ v1_xboole_0(u1_struct_0(A)) ) ).

fof(fc1_subset_1,axiom,
    ! [A] : ~ v1_xboole_0(k1_zfmisc_1(A)) ).

fof(fc1_xboole_0,axiom,
    v1_xboole_0(k1_xboole_0) ).

fof(fc4_subset_1,axiom,
    ! [A,B] :
      ( ( ~ v1_xboole_0(A)
        & ~ v1_xboole_0(B) )
     => ~ v1_xboole_0(k2_zfmisc_1(A,B)) ) ).

fof(free_g1_group_1,axiom,
    ! [A,B] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ! [C,D] :
          ( g1_group_1(A,B) = g1_group_1(C,D)
         => ( A = C
            & B = D ) ) ) ).

fof(rc1_funct_2,axiom,
    ! [A,B] :
    ? [C] :
      ( m1_relset_1(C,A,B)
      & v1_relat_1(C)
      & v1_funct_1(C)
      & v1_funct_2(C,A,B) ) ).

fof(rc1_subset_1,axiom,
    ! [A] :
      ( ~ v1_xboole_0(A)
     => ? [B] :
          ( m1_subset_1(B,k1_zfmisc_1(A))
          & ~ v1_xboole_0(B) ) ) ).

fof(rc1_xboole_0,axiom,
    ? [A] : v1_xboole_0(A) ).

fof(rc2_partfun1,axiom,
    ! [A,B] :
    ? [C] :
      ( m1_relset_1(C,A,B)
      & v1_relat_1(C)
      & v1_funct_1(C) ) ).

fof(rc2_subset_1,axiom,
    ! [A] :
    ? [B] :
      ( m1_subset_1(B,k1_zfmisc_1(A))
      & v1_xboole_0(B) ) ).

fof(rc2_xboole_0,axiom,
    ? [A] : ~ v1_xboole_0(A) ).

fof(rc3_struct_0,axiom,
    ? [A] :
      ( l1_struct_0(A)
      & ~ v3_struct_0(A) ) ).

fof(rc5_struct_0,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l1_struct_0(A) )
     => ? [B] :
          ( m1_subset_1(B,k1_zfmisc_1(u1_struct_0(A)))
          & ~ v1_xboole_0(B) ) ) ).

fof(redefinition_k2_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( v1_funct_1(C)
        & v1_funct_2(C,A,B)
        & m1_relset_1(C,A,B) )
     => k2_funct_2(A,B,C,D) = k9_relat_1(C,D) ) ).

fof(redefinition_k4_relset_1,axiom,
    ! [A,B,C] :
      ( m1_relset_1(C,A,B)
     => k4_relset_1(A,B,C) = k1_relat_1(C) ) ).

fof(redefinition_k8_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( ~ v1_xboole_0(A)
        & v1_funct_1(C)
        & v1_funct_2(C,A,B)
        & m1_relset_1(C,A,B)
        & m1_subset_1(D,A) )
     => k8_funct_2(A,B,C,D) = k1_funct_1(C,D) ) ).

fof(redefinition_m2_relset_1,axiom,
    ! [A,B,C] :
      ( m2_relset_1(C,A,B)
    <=> m1_relset_1(C,A,B) ) ).

fof(reflexivity_r1_tarski,axiom,
    ! [A,B] : r1_tarski(A,A) ).

fof(t116_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( v1_funct_1(D)
        & v1_funct_2(D,A,B)
        & m2_relset_1(D,A,B) )
     => ! [E] :
          ~ ( r2_hidden(E,k2_funct_2(A,B,D,C))
            & ! [F] :
                ( m1_subset_1(F,A)
               => ~ ( r2_hidden(F,C)
                    & E = k1_funct_1(D,F) ) ) ) ) ).

fof(t1_subset,axiom,
    ! [A,B] :
      ( r2_hidden(A,B)
     => m1_subset_1(A,B) ) ).

fof(t2_subset,axiom,
    ! [A,B] :
      ( m1_subset_1(A,B)
     => ( v1_xboole_0(B)
        | r2_hidden(A,B) ) ) ).

fof(t3_subset,axiom,
    ! [A,B] :
      ( m1_subset_1(A,k1_zfmisc_1(B))
    <=> r1_tarski(A,B) ) ).

fof(t41_group_6,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( ~ v3_struct_0(B)
            & v3_group_1(B)
            & v4_group_1(B)
            & l1_group_1(B) )
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(A))
             => ! [D] :
                  ( ( v1_funct_1(D)
                    & v1_funct_2(D,u1_struct_0(A),u1_struct_0(B))
                    & v1_group_6(D,A,B)
                    & m2_relset_1(D,u1_struct_0(A),u1_struct_0(B)) )
                 => k8_funct_2(u1_struct_0(A),u1_struct_0(B),D,k3_group_1(A,C)) = k3_group_1(B,k8_funct_2(u1_struct_0(A),u1_struct_0(B),D,C)) ) ) ) ) ).

fof(t43_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( v1_funct_1(D)
        & v1_funct_2(D,A,B)
        & m2_relset_1(D,A,B) )
     => ( B != k1_xboole_0
       => ! [E] :
            ( ? [F] :
                ( r2_hidden(F,A)
                & r2_hidden(F,C)
                & E = k1_funct_1(D,F) )
           => r2_hidden(E,k9_relat_1(D,C)) ) ) ) ).

fof(t4_subset,axiom,
    ! [A,B,C] :
      ( ( r2_hidden(A,B)
        & m1_subset_1(B,k1_zfmisc_1(C)) )
     => m1_subset_1(A,C) ) ).

fof(t55_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => r1_rlvect_1(B,k2_group_1(A)) ) ) ).

fof(t59_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(A))
             => ! [D] :
                  ( m1_group_2(D,A)
                 => ( ( r1_rlvect_1(D,B)
                      & r1_rlvect_1(D,C) )
                   => r1_rlvect_1(D,k1_group_1(A,B,C)) ) ) ) ) ) ).

fof(t5_subset,axiom,
    ! [A,B,C] :
      ~ ( r2_hidden(A,B)
        & m1_subset_1(B,k1_zfmisc_1(C))
        & v1_xboole_0(C) ) ).

fof(t60_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => ! [C] :
              ( m1_group_2(C,A)
             => ( r1_rlvect_1(C,B)
               => r1_rlvect_1(C,k3_group_1(A,B)) ) ) ) ) ).

fof(t61_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,k1_zfmisc_1(u1_struct_0(A)))
         => ~ ( B != k1_xboole_0
              & ! [C] :
                  ( m1_subset_1(C,u1_struct_0(A))
                 => ! [D] :
                      ( m1_subset_1(D,u1_struct_0(A))
                     => ( ( r2_hidden(C,B)
                          & r2_hidden(D,B) )
                       => r2_hidden(k1_group_1(A,C,D),B) ) ) )
              & ! [C] :
                  ( m1_subset_1(C,u1_struct_0(A))
                 => ( r2_hidden(C,B)
                   => r2_hidden(k3_group_1(A,C),B) ) )
              & ! [C] :
                  ( ( v1_group_1(C)
                    & m1_group_2(C,A) )
                 => u1_struct_0(C) != B ) ) ) ) ).

fof(t6_boole,axiom,
    ! [A] :
      ( v1_xboole_0(A)
     => A = k1_xboole_0 ) ).

fof(t7_boole,axiom,
    ! [A,B] :
      ~ ( r2_hidden(A,B)
        & v1_xboole_0(B) ) ).

fof(t8_boole,axiom,
    ! [A,B] :
      ~ ( v1_xboole_0(A)
        & A != B
        & v1_xboole_0(B) ) ).

%------------------------------------------------------------------------------
