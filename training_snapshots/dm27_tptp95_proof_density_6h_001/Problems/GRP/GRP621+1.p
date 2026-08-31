%------------------------------------------------------------------------------
% File     : GRP621+1 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Group of Inner Automorphisms T08
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Kor96] Kornilowicz (1996), On the Group of Inner Automorphism
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t8_autgroup [Urb08]

% Status   : Theorem
% Rating   : 0.43 v9.3.0, 0.55 v9.1.0, 0.52 v9.0.0, 0.53 v8.2.0, 0.50 v8.1.0, 0.58 v7.5.0, 0.66 v7.4.0, 0.57 v7.3.0, 0.62 v7.2.0, 0.59 v7.1.0, 0.57 v6.4.0, 0.58 v6.3.0, 0.54 v6.2.0, 0.64 v6.1.0, 0.80 v6.0.0, 0.83 v5.5.0, 0.85 v5.4.0, 0.86 v5.3.0, 0.89 v5.2.0, 0.85 v5.1.0, 0.86 v5.0.0, 0.88 v4.1.0, 0.91 v4.0.1, 0.87 v4.0.0, 0.88 v3.7.0, 0.95 v3.4.0
% Syntax   : Number of formulae    :   71 (  17 unt;   0 def)
%            Number of atoms       :  320 (   9 equ)
%            Maximal formula atoms :   24 (   4 avg)
%            Number of connectives :  293 (  44   ~;   1   |; 183   &)
%                                         (   6 <=>;  59  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   26 (   6 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :   26 (  24 usr;   1 prp; 0-4 aty)
%            Number of functors    :   10 (  10 usr;   1 con; 0-5 aty)
%            Number of variables   :  145 ( 123   !;  22   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Normal version: includes the axioms (which may be theorems from
%            other articles) and background that are possibly necessary.
%          : Translated by MPTP from the Mizar Mathematical Library 4.48.930.
%          : The problem encoding is based on set theory.
%------------------------------------------------------------------------------
fof(t8_autgroup,conjecture,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
         => ! [C] :
              ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
             => m2_fraenkel(k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),C,B),u1_struct_0(A),u1_struct_0(A),k1_autgroup(A)) ) ) ) ).

fof(abstractness_v1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => ( v1_group_1(A)
       => A = g1_group_1(u1_struct_0(A),u1_group_1(A)) ) ) ).

fof(antisymmetry_r2_hidden,axiom,
    ! [A,B] :
      ( r2_hidden(A,B)
     => ~ r2_hidden(B,A) ) ).

fof(cc1_fraenkel,axiom,
    ! [A] :
      ( v1_fraenkel(A)
     => ! [B] :
          ( m1_subset_1(B,A)
         => ( v1_relat_1(B)
            & v1_funct_1(B) ) ) ) ).

fof(cc1_funct_1,axiom,
    ! [A] :
      ( v1_xboole_0(A)
     => v1_funct_1(A) ) ).

fof(cc1_funct_2,axiom,
    ! [A,B,C] :
      ( m1_relset_1(C,A,B)
     => ( ( v1_funct_1(C)
          & v1_partfun1(C,A,B) )
       => ( v1_funct_1(C)
          & v1_funct_2(C,A,B) ) ) ) ).

fof(cc1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => ( ( ~ v3_struct_0(A)
          & v3_group_1(A) )
       => ( ~ v3_struct_0(A)
          & v2_group_1(A) ) ) ) ).

fof(cc1_relset_1,axiom,
    ! [A,B,C] :
      ( m1_subset_1(C,k1_zfmisc_1(k2_zfmisc_1(A,B)))
     => v1_relat_1(C) ) ).

fof(cc2_funct_1,axiom,
    ! [A] :
      ( ( v1_relat_1(A)
        & v1_xboole_0(A)
        & v1_funct_1(A) )
     => ( v1_relat_1(A)
        & v1_funct_1(A)
        & v2_funct_1(A) ) ) ).

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

fof(d1_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_fraenkel(B,u1_struct_0(A),u1_struct_0(A))
         => ( B = k1_autgroup(A)
          <=> ( ! [C] :
                  ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),B)
                 => ( v1_funct_1(C)
                    & v1_funct_2(C,u1_struct_0(A),u1_struct_0(A))
                    & v1_group_6(C,A,A)
                    & m2_relset_1(C,u1_struct_0(A),u1_struct_0(A)) ) )
              & ! [C] :
                  ( ( v1_funct_1(C)
                    & v1_funct_2(C,u1_struct_0(A),u1_struct_0(A))
                    & v1_group_6(C,A,A)
                    & m2_relset_1(C,u1_struct_0(A),u1_struct_0(A)) )
                 => ( r2_hidden(C,B)
                  <=> ( v2_funct_1(C)
                      & v3_group_6(C,A,A) ) ) ) ) ) ) ) ).

fof(dt_g1_group_1,axiom,
    ! [A,B] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ( v1_group_1(g1_group_1(A,B))
        & l1_group_1(g1_group_1(A,B)) ) ) ).

fof(dt_k1_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => m1_fraenkel(k1_autgroup(A),u1_struct_0(A),u1_struct_0(A)) ) ).

fof(dt_k1_xboole_0,axiom,
    $true ).

fof(dt_k1_zfmisc_1,axiom,
    $true ).

fof(dt_k2_zfmisc_1,axiom,
    $true ).

fof(dt_k5_relat_1,axiom,
    ! [A,B] :
      ( ( v1_relat_1(A)
        & v1_relat_1(B) )
     => v1_relat_1(k5_relat_1(A,B)) ) ).

fof(dt_k7_funct_2,axiom,
    ! [A,B,C,D,E] :
      ( ( ~ v1_xboole_0(B)
        & v1_funct_1(D)
        & v1_funct_2(D,A,B)
        & m1_relset_1(D,A,B)
        & v1_funct_1(E)
        & v1_funct_2(E,B,C)
        & m1_relset_1(E,B,C) )
     => ( v1_funct_1(k7_funct_2(A,B,C,D,E))
        & v1_funct_2(k7_funct_2(A,B,C,D,E),A,C)
        & m2_relset_1(k7_funct_2(A,B,C,D,E),A,C) ) ) ).

fof(dt_k8_group_6,axiom,
    ! [A,B,C,D,E] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & ~ v3_struct_0(B)
        & v3_group_1(B)
        & v4_group_1(B)
        & l1_group_1(B)
        & ~ v3_struct_0(C)
        & v3_group_1(C)
        & v4_group_1(C)
        & l1_group_1(C)
        & v1_funct_1(D)
        & v1_funct_2(D,u1_struct_0(A),u1_struct_0(B))
        & v1_group_6(D,A,B)
        & m1_relset_1(D,u1_struct_0(A),u1_struct_0(B))
        & v1_funct_1(E)
        & v1_funct_2(E,u1_struct_0(B),u1_struct_0(C))
        & v1_group_6(E,B,C)
        & m1_relset_1(E,u1_struct_0(B),u1_struct_0(C)) )
     => ( v1_funct_1(k8_group_6(A,B,C,D,E))
        & v1_funct_2(k8_group_6(A,B,C,D,E),u1_struct_0(A),u1_struct_0(C))
        & v1_group_6(k8_group_6(A,B,C,D,E),A,C)
        & m2_relset_1(k8_group_6(A,B,C,D,E),u1_struct_0(A),u1_struct_0(C)) ) ) ).

fof(dt_l1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => l1_struct_0(A) ) ).

fof(dt_l1_struct_0,axiom,
    $true ).

fof(dt_m1_fraenkel,axiom,
    ! [A,B,C] :
      ( m1_fraenkel(C,A,B)
     => ( ~ v1_xboole_0(C)
        & v1_fraenkel(C) ) ) ).

fof(dt_m1_relset_1,axiom,
    $true ).

fof(dt_m1_subset_1,axiom,
    $true ).

fof(dt_m2_fraenkel,axiom,
    ! [A,B,C] :
      ( ( ~ v1_xboole_0(B)
        & m1_fraenkel(C,A,B) )
     => ! [D] :
          ( m2_fraenkel(D,A,B,C)
         => ( v1_funct_1(D)
            & v1_funct_2(D,A,B)
            & m2_relset_1(D,A,B) ) ) ) ).

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

fof(existence_m1_fraenkel,axiom,
    ! [A,B] :
    ? [C] : m1_fraenkel(C,A,B) ).

fof(existence_m1_relset_1,axiom,
    ! [A,B] :
    ? [C] : m1_relset_1(C,A,B) ).

fof(existence_m1_subset_1,axiom,
    ! [A] :
    ? [B] : m1_subset_1(B,A) ).

fof(existence_m2_fraenkel,axiom,
    ! [A,B,C] :
      ( ( ~ v1_xboole_0(B)
        & m1_fraenkel(C,A,B) )
     => ? [D] : m2_fraenkel(D,A,B,C) ) ).

fof(existence_m2_relset_1,axiom,
    ! [A,B] :
    ? [C] : m2_relset_1(C,A,B) ).

fof(fc1_funct_1,axiom,
    ! [A,B] :
      ( ( v1_relat_1(A)
        & v1_funct_1(A)
        & v1_relat_1(B)
        & v1_funct_1(B) )
     => ( v1_relat_1(k5_relat_1(A,B))
        & v1_funct_1(k5_relat_1(A,B)) ) ) ).

fof(fc1_group_1,axiom,
    ! [A,B] :
      ( ( ~ v1_xboole_0(A)
        & v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ( ~ v3_struct_0(g1_group_1(A,B))
        & v1_group_1(g1_group_1(A,B)) ) ) ).

fof(fc1_struct_0,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l1_struct_0(A) )
     => ~ v1_xboole_0(u1_struct_0(A)) ) ).

fof(fc1_xboole_0,axiom,
    v1_xboole_0(k1_xboole_0) ).

fof(free_g1_group_1,axiom,
    ! [A,B] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ! [C,D] :
          ( g1_group_1(A,B) = g1_group_1(C,D)
         => ( A = C
            & B = D ) ) ) ).

fof(rc1_fraenkel,axiom,
    ? [A] :
      ( ~ v1_xboole_0(A)
      & v1_fraenkel(A) ) ).

fof(rc1_funct_1,axiom,
    ? [A] :
      ( v1_relat_1(A)
      & v1_funct_1(A) ) ).

fof(rc1_funct_2,axiom,
    ! [A,B] :
    ? [C] :
      ( m1_relset_1(C,A,B)
      & v1_relat_1(C)
      & v1_funct_1(C)
      & v1_funct_2(C,A,B) ) ).

fof(rc1_group_1,axiom,
    ? [A] :
      ( l1_group_1(A)
      & v1_group_1(A) ) ).

fof(rc1_partfun1,axiom,
    ? [A] :
      ( v1_relat_1(A)
      & v1_funct_1(A)
      & v2_funct_1(A)
      & v1_xboole_0(A) ) ).

fof(rc1_xboole_0,axiom,
    ? [A] : v1_xboole_0(A) ).

fof(rc2_funct_1,axiom,
    ? [A] :
      ( v1_relat_1(A)
      & v1_xboole_0(A)
      & v1_funct_1(A) ) ).

fof(rc2_group_1,axiom,
    ? [A] :
      ( l1_group_1(A)
      & ~ v3_struct_0(A)
      & v1_group_1(A) ) ).

fof(rc2_group_6,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & ~ v3_struct_0(B)
        & v3_group_1(B)
        & v4_group_1(B)
        & l1_group_1(B) )
     => ? [C] :
          ( m1_relset_1(C,u1_struct_0(A),u1_struct_0(B))
          & ~ v1_xboole_0(C)
          & v1_relat_1(C)
          & v1_funct_1(C)
          & v1_funct_2(C,u1_struct_0(A),u1_struct_0(B))
          & v1_partfun1(C,u1_struct_0(A),u1_struct_0(B))
          & v1_group_6(C,A,B) ) ) ).

fof(rc2_partfun1,axiom,
    ! [A,B] :
    ? [C] :
      ( m1_relset_1(C,A,B)
      & v1_relat_1(C)
      & v1_funct_1(C) ) ).

fof(rc2_xboole_0,axiom,
    ? [A] : ~ v1_xboole_0(A) ).

fof(rc3_funct_1,axiom,
    ? [A] :
      ( v1_relat_1(A)
      & v1_funct_1(A)
      & v2_funct_1(A) ) ).

fof(rc3_group_1,axiom,
    ? [A] :
      ( l1_group_1(A)
      & ~ v3_struct_0(A)
      & v1_group_1(A)
      & v2_group_1(A)
      & v3_group_1(A)
      & v4_group_1(A) ) ).

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

fof(redefinition_k7_funct_2,axiom,
    ! [A,B,C,D,E] :
      ( ( ~ v1_xboole_0(B)
        & v1_funct_1(D)
        & v1_funct_2(D,A,B)
        & m1_relset_1(D,A,B)
        & v1_funct_1(E)
        & v1_funct_2(E,B,C)
        & m1_relset_1(E,B,C) )
     => k7_funct_2(A,B,C,D,E) = k5_relat_1(D,E) ) ).

fof(redefinition_k8_group_6,axiom,
    ! [A,B,C,D,E] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & ~ v3_struct_0(B)
        & v3_group_1(B)
        & v4_group_1(B)
        & l1_group_1(B)
        & ~ v3_struct_0(C)
        & v3_group_1(C)
        & v4_group_1(C)
        & l1_group_1(C)
        & v1_funct_1(D)
        & v1_funct_2(D,u1_struct_0(A),u1_struct_0(B))
        & v1_group_6(D,A,B)
        & m1_relset_1(D,u1_struct_0(A),u1_struct_0(B))
        & v1_funct_1(E)
        & v1_funct_2(E,u1_struct_0(B),u1_struct_0(C))
        & v1_group_6(E,B,C)
        & m1_relset_1(E,u1_struct_0(B),u1_struct_0(C)) )
     => k8_group_6(A,B,C,D,E) = k5_relat_1(D,E) ) ).

fof(redefinition_m2_fraenkel,axiom,
    ! [A,B,C] :
      ( ( ~ v1_xboole_0(B)
        & m1_fraenkel(C,A,B) )
     => ! [D] :
          ( m2_fraenkel(D,A,B,C)
        <=> m1_subset_1(D,C) ) ) ).

fof(redefinition_m2_relset_1,axiom,
    ! [A,B,C] :
      ( m2_relset_1(C,A,B)
    <=> m1_relset_1(C,A,B) ) ).

fof(reflexivity_r1_tarski,axiom,
    ! [A,B] : r1_tarski(A,A) ).

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

fof(t4_subset,axiom,
    ! [A,B,C] :
      ( ( r2_hidden(A,B)
        & m1_subset_1(B,k1_zfmisc_1(C)) )
     => m1_subset_1(A,C) ) ).

fof(t5_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_funct_1(B)
            & v1_funct_2(B,u1_struct_0(A),u1_struct_0(A))
            & v1_group_6(B,A,A)
            & m2_relset_1(B,u1_struct_0(A),u1_struct_0(A)) )
         => ( r2_hidden(B,k1_autgroup(A))
          <=> v4_group_6(B,A,A) ) ) ) ).

fof(t5_subset,axiom,
    ! [A,B,C] :
      ~ ( r2_hidden(A,B)
        & m1_subset_1(B,k1_zfmisc_1(C))
        & v1_xboole_0(C) ) ).

fof(t6_boole,axiom,
    ! [A] :
      ( v1_xboole_0(A)
     => A = k1_xboole_0 ) ).

fof(t74_group_6,axiom,
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
              ( ( ~ v3_struct_0(C)
                & v3_group_1(C)
                & v4_group_1(C)
                & l1_group_1(C) )
             => ! [D] :
                  ( ( v1_funct_1(D)
                    & v1_funct_2(D,u1_struct_0(A),u1_struct_0(B))
                    & v1_group_6(D,A,B)
                    & m2_relset_1(D,u1_struct_0(A),u1_struct_0(B)) )
                 => ! [E] :
                      ( ( v1_funct_1(E)
                        & v1_funct_2(E,u1_struct_0(B),u1_struct_0(C))
                        & v1_group_6(E,B,C)
                        & m2_relset_1(E,u1_struct_0(B),u1_struct_0(C)) )
                     => ( ( v4_group_6(D,A,B)
                          & v4_group_6(E,B,C) )
                       => v4_group_6(k8_group_6(A,B,C,D,E),A,C) ) ) ) ) ) ) ).

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
