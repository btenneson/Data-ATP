%------------------------------------------------------------------------------
% File     : GRP649+1 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Lattice of Subgroups of a Group T32
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Gan96] Ganczarski (1996), On the Lattice of Subgroups of a Gr
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t32_latsubgr [Urb08]

% Status   : Theorem
% Rating   : 1.00 v3.4.0
% Syntax   : Number of formulae    :   94 (  24 unt;   0 def)
%            Number of atoms       :  374 (  26 equ)
%            Maximal formula atoms :   16 (   3 avg)
%            Number of connectives :  339 (  59   ~;   2   |; 175   &)
%                                         (  11 <=>;  92  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   14 (   6 avg)
%            Maximal term depth    :    5 (   1 avg)
%            Number of predicates  :   38 (  36 usr;   1 prp; 0-3 aty)
%            Number of functors    :   22 (  22 usr;   1 con; 0-4 aty)
%            Number of variables   :  186 ( 166   !;  20   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Normal version: includes the axioms (which may be theorems from
%            other articles) and background that are possibly necessary.
%          : Translated by MPTP from the Mizar Mathematical Library 4.48.930.
%          : The problem encoding is based on set theory.
%------------------------------------------------------------------------------
fof(t32_latsubgr,conjecture,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => v4_lattice3(k11_group_4(A)) ) ).

fof(abstractness_v1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => ( v1_group_1(A)
       => A = g1_group_1(u1_struct_0(A),u1_group_1(A)) ) ) ).

fof(abstractness_v3_lattices,axiom,
    ! [A] :
      ( l3_lattices(A)
     => ( v3_lattices(A)
       => A = g3_lattices(u1_struct_0(A),u2_lattices(A),u1_lattices(A)) ) ) ).

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

fof(d13_group_4,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => k11_group_4(A) = g3_lattices(k1_group_3(A),k9_group_4(A),k10_group_4(A)) ) ).

fof(d16_lattice3,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l3_lattices(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => ! [C] :
              ( r3_lattice3(A,B,C)
            <=> ! [D] :
                  ( m1_subset_1(D,u1_struct_0(A))
                 => ( r2_hidden(D,C)
                   => r1_lattices(A,B,D) ) ) ) ) ) ).

fof(d1_group_3,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( B = k1_group_3(A)
        <=> ! [C] :
              ( r2_hidden(C,B)
            <=> ( v1_group_1(C)
                & m1_group_2(C,A) ) ) ) ) ).

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

fof(d2_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( ~ v1_xboole_0(B)
            & m1_subset_1(B,k1_zfmisc_1(k1_group_3(A))) )
         => ! [C] :
              ( ( v1_group_1(C)
                & m1_group_2(C,A) )
             => ( C = k2_latsubgr(A,B)
              <=> u1_struct_0(C) = k6_setfam_1(u1_struct_0(A),k2_funct_2(k1_group_3(A),k1_zfmisc_1(u1_struct_0(A)),k1_latsubgr(A),B)) ) ) ) ) ).

fof(d6_vectsp_8,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l3_lattices(A) )
     => ( v4_lattice3(A)
      <=> ! [B] :
            ( m1_subset_1(B,k1_zfmisc_1(u1_struct_0(A)))
           => ? [C] :
                ( m1_subset_1(C,u1_struct_0(A))
                & r3_lattice3(A,C,B)
                & ! [D] :
                    ( m1_subset_1(D,u1_struct_0(A))
                   => ( r3_lattice3(A,D,B)
                     => r1_lattices(A,D,C) ) ) ) ) ) ) ).

fof(dt_g1_group_1,axiom,
    ! [A,B] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A) )
     => ( v1_group_1(g1_group_1(A,B))
        & l1_group_1(g1_group_1(A,B)) ) ) ).

fof(dt_g3_lattices,axiom,
    ! [A,B,C] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A)
        & v1_funct_1(C)
        & v1_funct_2(C,k2_zfmisc_1(A,A),A)
        & m1_relset_1(C,k2_zfmisc_1(A,A),A) )
     => ( v3_lattices(g3_lattices(A,B,C))
        & l3_lattices(g3_lattices(A,B,C)) ) ) ).

fof(dt_k10_group_4,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( v1_funct_1(k10_group_4(A))
        & v1_funct_2(k10_group_4(A),k2_zfmisc_1(k1_group_3(A),k1_group_3(A)),k1_group_3(A))
        & m2_relset_1(k10_group_4(A),k2_zfmisc_1(k1_group_3(A),k1_group_3(A)),k1_group_3(A)) ) ) ).

fof(dt_k11_group_4,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( ~ v3_struct_0(k11_group_4(A))
        & v3_lattices(k11_group_4(A))
        & v10_lattices(k11_group_4(A))
        & l3_lattices(k11_group_4(A)) ) ) ).

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

fof(dt_k1_setfam_1,axiom,
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

fof(dt_k2_latsubgr,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & ~ v1_xboole_0(B)
        & m1_subset_1(B,k1_zfmisc_1(k1_group_3(A))) )
     => ( v1_group_1(k2_latsubgr(A,B))
        & m1_group_2(k2_latsubgr(A,B),A) ) ) ).

fof(dt_k2_zfmisc_1,axiom,
    $true ).

fof(dt_k6_lattices,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & l2_lattices(A) )
     => m1_subset_1(k6_lattices(A),u1_struct_0(A)) ) ).

fof(dt_k6_setfam_1,axiom,
    ! [A,B] :
      ( m1_subset_1(B,k1_zfmisc_1(k1_zfmisc_1(A)))
     => m1_subset_1(k6_setfam_1(A,B),k1_zfmisc_1(A)) ) ).

fof(dt_k8_funct_2,axiom,
    ! [A,B,C,D] :
      ( ( ~ v1_xboole_0(A)
        & v1_funct_1(C)
        & v1_funct_2(C,A,B)
        & m1_relset_1(C,A,B)
        & m1_subset_1(D,A) )
     => m1_subset_1(k8_funct_2(A,B,C,D),B) ) ).

fof(dt_k9_group_4,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( v1_funct_1(k9_group_4(A))
        & v1_funct_2(k9_group_4(A),k2_zfmisc_1(k1_group_3(A),k1_group_3(A)),k1_group_3(A))
        & m2_relset_1(k9_group_4(A),k2_zfmisc_1(k1_group_3(A),k1_group_3(A)),k1_group_3(A)) ) ) ).

fof(dt_k9_relat_1,axiom,
    $true ).

fof(dt_l1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => l1_struct_0(A) ) ).

fof(dt_l1_lattices,axiom,
    ! [A] :
      ( l1_lattices(A)
     => l1_struct_0(A) ) ).

fof(dt_l1_struct_0,axiom,
    $true ).

fof(dt_l2_lattices,axiom,
    ! [A] :
      ( l2_lattices(A)
     => l1_struct_0(A) ) ).

fof(dt_l3_lattices,axiom,
    ! [A] :
      ( l3_lattices(A)
     => ( l1_lattices(A)
        & l2_lattices(A) ) ) ).

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

fof(dt_m2_subset_1,axiom,
    ! [A,B] :
      ( ( ~ v1_xboole_0(A)
        & ~ v1_xboole_0(B)
        & m1_subset_1(B,k1_zfmisc_1(A)) )
     => ! [C] :
          ( m2_subset_1(C,A,B)
         => m1_subset_1(C,A) ) ) ).

fof(dt_u1_group_1,axiom,
    ! [A] :
      ( l1_group_1(A)
     => ( v1_funct_1(u1_group_1(A))
        & v1_funct_2(u1_group_1(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A))
        & m2_relset_1(u1_group_1(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A)) ) ) ).

fof(dt_u1_lattices,axiom,
    ! [A] :
      ( l1_lattices(A)
     => ( v1_funct_1(u1_lattices(A))
        & v1_funct_2(u1_lattices(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A))
        & m2_relset_1(u1_lattices(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A)) ) ) ).

fof(dt_u1_struct_0,axiom,
    $true ).

fof(dt_u2_lattices,axiom,
    ! [A] :
      ( l2_lattices(A)
     => ( v1_funct_1(u2_lattices(A))
        & v1_funct_2(u2_lattices(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A))
        & m2_relset_1(u2_lattices(A),k2_zfmisc_1(u1_struct_0(A),u1_struct_0(A)),u1_struct_0(A)) ) ) ).

fof(existence_l1_group_1,axiom,
    ? [A] : l1_group_1(A) ).

fof(existence_l1_lattices,axiom,
    ? [A] : l1_lattices(A) ).

fof(existence_l1_struct_0,axiom,
    ? [A] : l1_struct_0(A) ).

fof(existence_l2_lattices,axiom,
    ? [A] : l2_lattices(A) ).

fof(existence_l3_lattices,axiom,
    ? [A] : l3_lattices(A) ).

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

fof(existence_m2_subset_1,axiom,
    ! [A,B] :
      ( ( ~ v1_xboole_0(A)
        & ~ v1_xboole_0(B)
        & m1_subset_1(B,k1_zfmisc_1(A)) )
     => ? [C] : m2_subset_1(C,A,B) ) ).

fof(fc1_group_3,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ~ v1_xboole_0(k1_group_3(A)) ) ).

fof(fc1_group_4,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( ~ v3_struct_0(k11_group_4(A))
        & v3_lattices(k11_group_4(A))
        & v4_lattices(k11_group_4(A))
        & v5_lattices(k11_group_4(A))
        & v6_lattices(k11_group_4(A))
        & v7_lattices(k11_group_4(A))
        & v8_lattices(k11_group_4(A))
        & v9_lattices(k11_group_4(A))
        & v10_lattices(k11_group_4(A))
        & v13_lattices(k11_group_4(A))
        & v14_lattices(k11_group_4(A))
        & v15_lattices(k11_group_4(A)) ) ) ).

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

fof(free_g3_lattices,axiom,
    ! [A,B,C] :
      ( ( v1_funct_1(B)
        & v1_funct_2(B,k2_zfmisc_1(A,A),A)
        & m1_relset_1(B,k2_zfmisc_1(A,A),A)
        & v1_funct_1(C)
        & v1_funct_2(C,k2_zfmisc_1(A,A),A)
        & m1_relset_1(C,k2_zfmisc_1(A,A),A) )
     => ! [D,E,F] :
          ( g3_lattices(A,B,C) = g3_lattices(D,E,F)
         => ( A = D
            & B = E
            & C = F ) ) ) ).

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

fof(redefinition_k6_setfam_1,axiom,
    ! [A,B] :
      ( m1_subset_1(B,k1_zfmisc_1(k1_zfmisc_1(A)))
     => k6_setfam_1(A,B) = k1_setfam_1(B) ) ).

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

fof(redefinition_m2_subset_1,axiom,
    ! [A,B] :
      ( ( ~ v1_xboole_0(A)
        & ~ v1_xboole_0(B)
        & m1_subset_1(B,k1_zfmisc_1(A)) )
     => ! [C] :
          ( m2_subset_1(C,A,B)
        <=> m1_subset_1(C,B) ) ) ).

fof(redefinition_r3_lattices,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v6_lattices(A)
        & v8_lattices(A)
        & v9_lattices(A)
        & l3_lattices(A)
        & m1_subset_1(B,u1_struct_0(A))
        & m1_subset_1(C,u1_struct_0(A)) )
     => ( r3_lattices(A,B,C)
      <=> r1_lattices(A,B,C) ) ) ).

fof(reflexivity_r1_tarski,axiom,
    ! [A,B] : r1_tarski(A,A) ).

fof(reflexivity_r3_lattices,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v6_lattices(A)
        & v8_lattices(A)
        & v9_lattices(A)
        & l3_lattices(A)
        & m1_subset_1(B,u1_struct_0(A))
        & m1_subset_1(C,u1_struct_0(A)) )
     => r3_lattices(A,B,B) ) ).

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

fof(t30_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ! [C] :
              ( m1_group_2(C,A)
             => ! [D] :
                  ( m1_subset_1(D,u1_struct_0(k11_group_4(A)))
                 => ! [E] :
                      ( m1_subset_1(E,u1_struct_0(k11_group_4(A)))
                     => ( ( D = B
                          & E = C )
                       => ( r3_lattices(k11_group_4(A),D,E)
                        <=> r1_tarski(u1_struct_0(B),u1_struct_0(C)) ) ) ) ) ) ) ) ).

fof(t3_subset,axiom,
    ! [A,B] :
      ( m1_subset_1(A,k1_zfmisc_1(B))
    <=> r1_tarski(A,B) ) ).

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

fof(t45_lattices,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v10_lattices(A)
        & v14_lattices(A)
        & l3_lattices(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => r3_lattices(A,B,k6_lattices(A)) ) ) ).

fof(t4_setfam_1,axiom,
    ! [A,B] :
      ( r2_hidden(A,B)
     => r1_tarski(k1_setfam_1(B),A) ) ).

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

fof(t6_setfam_1,axiom,
    ! [A,B] :
      ( ! [C] :
          ( r2_hidden(C,A)
         => r1_tarski(B,C) )
     => ( A = k1_xboole_0
        | r1_tarski(B,k1_setfam_1(A)) ) ) ).

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
