%------------------------------------------------------------------------------
% File     : GRP645+1 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Lattice of Subgroups of a Group T24
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Gan96] Ganczarski (1996), On the Lattice of Subgroups of a Gr
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t24_latsubgr [Urb08]

% Status   : Theorem
% Rating   : 0.26 v9.3.0, 0.24 v9.1.0, 0.27 v9.0.0, 0.31 v8.2.0, 0.28 v7.5.0, 0.34 v7.4.0, 0.17 v7.3.0, 0.21 v7.2.0, 0.17 v7.1.0, 0.22 v7.0.0, 0.23 v6.4.0, 0.27 v6.3.0, 0.25 v6.2.0, 0.28 v6.1.0, 0.37 v6.0.0, 0.35 v5.5.0, 0.37 v5.4.0, 0.43 v5.3.0, 0.48 v5.2.0, 0.30 v5.1.0, 0.33 v5.0.0, 0.46 v4.1.0, 0.43 v4.0.0, 0.46 v3.7.0, 0.40 v3.5.0, 0.42 v3.4.0
% Syntax   : Number of formulae    :   62 (  23 unt;   0 def)
%            Number of atoms       :  198 (  15 equ)
%            Maximal formula atoms :   11 (   3 avg)
%            Number of connectives :  170 (  34   ~;   1   |;  88   &)
%                                         (   3 <=>;  44  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   10 (   5 avg)
%            Maximal term depth    :    4 (   1 avg)
%            Number of predicates  :   19 (  17 usr;   1 prp; 0-3 aty)
%            Number of functors    :   12 (  12 usr;   1 con; 0-3 aty)
%            Number of variables   :  109 (  95   !;  14   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Normal version: includes the axioms (which may be theorems from
%            other articles) and background that are possibly necessary.
%          : Translated by MPTP from the Mizar Mathematical Library 4.48.930.
%          : The problem encoding is based on set theory.
%------------------------------------------------------------------------------
fof(t24_latsubgr,conjecture,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => ! [C] :
              ( ( v1_group_1(C)
                & m1_group_2(C,A) )
             => k1_funct_1(k1_latsubgr(A),k9_group_2(A,B,C)) = k3_xboole_0(k1_funct_1(k1_latsubgr(A),B),k1_funct_1(k1_latsubgr(A),C)) ) ) ) ).

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

fof(commutativity_k3_xboole_0,axiom,
    ! [A,B] : k3_xboole_0(A,B) = k3_xboole_0(B,A) ).

fof(commutativity_k9_group_2,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A)
        & m1_group_2(C,A) )
     => k9_group_2(A,B,C) = k9_group_2(A,C,B) ) ).

fof(d1_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_funct_1(B)
            & v1_funct_2(B,k1_group_3(A),k1_zfmisc_1(u1_struct_0(A)))
            & m2_relset_1(B,k1_group_3(A),k1_zfmisc_1(u1_struct_0(A))) )
         => ( B = k1_latsubgr(A)
          <=> ! [C] :
                ( ( v1_group_1(C)
                  & m1_group_2(C,A) )
               => k1_funct_1(B,C) = u1_struct_0(C) ) ) ) ) ).

fof(dt_g1_group_1,axiom,
    ! [A,B] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ( v1_group_1(g1_group_1(A,B))
        & l1_group_1(g1_group_1(A,B)) ) ) ).

fof(dt_k1_funct_1,axiom,
    $true ).

fof(dt_k1_group_3,axiom,
    $true ).

fof(dt_k1_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( v1_funct_1(k1_latsubgr(A))
        & v1_funct_2(k1_latsubgr(A),k1_group_3(A),k1_zfmisc_1(u1_struct_0(A)))
        & m2_relset_1(k1_latsubgr(A),k1_group_3(A),k1_zfmisc_1(u1_struct_0(A))) ) ) ).

fof(dt_k1_xboole_0,axiom,
    $true ).

fof(dt_k1_zfmisc_1,axiom,
    $true ).

fof(dt_k2_zfmisc_1,axiom,
    $true ).

fof(dt_k3_xboole_0,axiom,
    $true ).

fof(dt_k8_group_2,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A)
        & m1_group_2(C,A) )
     => ( v1_group_1(k8_group_2(A,B,C))
        & m1_group_2(k8_group_2(A,B,C),A) ) ) ).

fof(dt_k9_group_2,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A)
        & m1_group_2(C,A) )
     => ( v1_group_1(k9_group_2(A,B,C))
        & m1_group_2(k9_group_2(A,B,C),A) ) ) ).

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

fof(fc1_group_3,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ~ v1_xboole_0(k1_group_3(A)) ) ).

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

fof(idempotence_k3_xboole_0,axiom,
    ! [A,B] : k3_xboole_0(A,A) = A ).

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

fof(redefinition_k9_group_2,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A)
        & m1_group_2(C,A) )
     => k9_group_2(A,B,C) = k8_group_2(A,B,C) ) ).

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

fof(t23_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => ! [C] :
              ( ( v1_group_1(C)
                & m1_group_2(C,A) )
             => u1_struct_0(k9_group_2(A,B,C)) = k3_xboole_0(k1_funct_1(k1_latsubgr(A),B),k1_funct_1(k1_latsubgr(A),C)) ) ) ) ).

fof(t2_boole,axiom,
    ! [A] : k3_xboole_0(A,k1_xboole_0) = k1_xboole_0 ).

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

fof(t5_subset,axiom,
    ! [A,B,C] :
      ~ ( r2_hidden(A,B)
        & m1_subset_1(B,k1_zfmisc_1(C))
        & v1_xboole_0(C) ) ).

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
