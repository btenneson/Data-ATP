%------------------------------------------------------------------------------
% File     : GRP637+1 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Lattice of Subgroups of a Group T10
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Gan96] Ganczarski (1996), On the Lattice of Subgroups of a Gr
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t10_latsubgr [Urb08]

% Status   : Theorem
% Rating   : 0.30 v9.3.0, 0.39 v9.0.0, 0.42 v8.2.0, 0.39 v8.1.0, 0.42 v7.5.0, 0.44 v7.4.0, 0.30 v7.3.0, 0.41 v7.2.0, 0.38 v7.1.0, 0.35 v7.0.0, 0.33 v6.4.0, 0.38 v6.2.0, 0.44 v6.1.0, 0.53 v6.0.0, 0.43 v5.5.0, 0.52 v5.4.0, 0.50 v5.3.0, 0.59 v5.2.0, 0.50 v5.1.0, 0.52 v5.0.0, 0.58 v4.1.0, 0.57 v4.0.0, 0.62 v3.7.0, 0.55 v3.5.0, 0.63 v3.4.0
% Syntax   : Number of formulae    :   55 (  19 unt;   0 def)
%            Number of atoms       :  177 (   6 equ)
%            Maximal formula atoms :   20 (   3 avg)
%            Number of connectives :  154 (  32   ~;   1   |;  71   &)
%                                         (   4 <=>;  46  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   18 (   5 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :   20 (  18 usr;   1 prp; 0-3 aty)
%            Number of functors    :    8 (   8 usr;   1 con; 0-4 aty)
%            Number of variables   :  106 (  91   !;  15   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Normal version: includes the axioms (which may be theorems from
%            other articles) and background that are possibly necessary.
%          : Translated by MPTP from the Mizar Mathematical Library 4.48.930.
%          : The problem encoding is based on set theory.
%------------------------------------------------------------------------------
fof(t10_latsubgr,conjecture,
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
                 => ! [E] :
                      ( m1_group_2(E,A)
                     => ! [F] :
                          ( m1_group_2(F,B)
                         => ! [G] :
                              ( m1_group_2(G,B)
                             => ( ( u1_struct_0(F) = k2_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(D))
                                  & u1_struct_0(G) = k2_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(E))
                                  & m1_group_6(D,A,E) )
                               => m1_group_6(F,B,G) ) ) ) ) ) ) ) ) ).

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

fof(d5_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( ~ v3_struct_0(B)
            & v3_group_1(B)
            & l1_group_1(B) )
         => ( m1_group_2(B,A)
          <=> ( r1_tarski(u1_struct_0(B),u1_struct_0(A))
              & u1_group_1(B) = k1_realset1(u1_group_1(A),u1_struct_0(B)) ) ) ) ) ).

fof(dt_k1_realset1,axiom,
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

fof(dt_k2_zfmisc_1,axiom,
    $true ).

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

fof(dt_m1_group_6,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A) )
     => ! [C] :
          ( m1_group_6(C,A,B)
         => m1_group_2(C,A) ) ) ).

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

fof(existence_m1_group_6,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A) )
     => ? [C] : m1_group_6(C,A,B) ) ).

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

fof(redefinition_m1_group_6,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_group_2(B,A) )
     => ! [C] :
          ( m1_group_6(C,A,B)
        <=> m1_group_2(C,B) ) ) ).

fof(redefinition_m2_relset_1,axiom,
    ! [A,B,C] :
      ( m2_relset_1(C,A,B)
    <=> m1_relset_1(C,A,B) ) ).

fof(reflexivity_r1_tarski,axiom,
    ! [A,B] : r1_tarski(A,A) ).

fof(t156_relat_1,axiom,
    ! [A,B,C] :
      ( v1_relat_1(C)
     => ( r1_tarski(A,B)
       => r1_tarski(k9_relat_1(C,A),k9_relat_1(C,B)) ) ) ).

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

fof(t5_subset,axiom,
    ! [A,B,C] :
      ~ ( r2_hidden(A,B)
        & m1_subset_1(B,k1_zfmisc_1(C))
        & v1_xboole_0(C) ) ).

fof(t66_group_2,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ! [C] :
              ( m1_group_2(C,A)
             => ( r1_tarski(u1_struct_0(B),u1_struct_0(C))
               => m1_group_2(B,C) ) ) ) ) ).

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
