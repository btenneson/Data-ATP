%------------------------------------------------------------------------------
% File     : GRP637+2 : TPTP v9.3.1. Released v3.4.0.
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
% Rating   : 0.96 v9.3.0, 0.97 v9.0.0, 1.00 v8.1.0, 0.97 v7.5.0, 1.00 v7.3.0, 0.97 v7.1.0, 0.96 v7.0.0, 1.00 v3.4.0
% Syntax   : Number of formulae    : 5648 (1551 unt;   0 def)
%            Number of atoms       : 31164 (3898 equ)
%            Maximal formula atoms :   49 (   5 avg)
%            Number of connectives : 29376 (3860   ~; 212   |;15082   &)
%                                         ( 949 <=>;9273  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   36 (   6 avg)
%            Maximal term depth    :    6 (   1 avg)
%            Number of predicates  :  325 ( 323 usr;   1 prp; 0-4 aty)
%            Number of functors    :  710 ( 710 usr; 182 con; 0-9 aty)
%            Number of variables   : 13232 (12611   !; 621   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Bushy version: includes all articles that contribute axioms to the
%            Normal version.
%          : Translated by MPTP from the Mizar Mathematical Library 4.48.930.
%          : The problem encoding is based on set theory.
%------------------------------------------------------------------------------
include('Axioms/SET007/SET007+0.ax').
include('Axioms/SET007/SET007+1.ax').
include('Axioms/SET007/SET007+2.ax').
include('Axioms/SET007/SET007+3.ax').
include('Axioms/SET007/SET007+4.ax').
include('Axioms/SET007/SET007+5.ax').
include('Axioms/SET007/SET007+6.ax').
include('Axioms/SET007/SET007+7.ax').
include('Axioms/SET007/SET007+8.ax').
include('Axioms/SET007/SET007+9.ax').
include('Axioms/SET007/SET007+10.ax').
include('Axioms/SET007/SET007+11.ax').
include('Axioms/SET007/SET007+13.ax').
include('Axioms/SET007/SET007+14.ax').
include('Axioms/SET007/SET007+16.ax').
include('Axioms/SET007/SET007+17.ax').
include('Axioms/SET007/SET007+18.ax').
include('Axioms/SET007/SET007+20.ax').
include('Axioms/SET007/SET007+22.ax').
include('Axioms/SET007/SET007+23.ax').
include('Axioms/SET007/SET007+25.ax').
include('Axioms/SET007/SET007+26.ax').
include('Axioms/SET007/SET007+31.ax').
include('Axioms/SET007/SET007+32.ax').
include('Axioms/SET007/SET007+35.ax').
include('Axioms/SET007/SET007+40.ax').
include('Axioms/SET007/SET007+48.ax').
include('Axioms/SET007/SET007+54.ax').
include('Axioms/SET007/SET007+55.ax').
include('Axioms/SET007/SET007+59.ax').
include('Axioms/SET007/SET007+60.ax').
include('Axioms/SET007/SET007+71.ax').
include('Axioms/SET007/SET007+117.ax').
include('Axioms/SET007/SET007+200.ax').
include('Axioms/SET007/SET007+205.ax').
include('Axioms/SET007/SET007+210.ax').
include('Axioms/SET007/SET007+212.ax').
include('Axioms/SET007/SET007+213.ax').
include('Axioms/SET007/SET007+218.ax').
include('Axioms/SET007/SET007+242.ax').
include('Axioms/SET007/SET007+246.ax').
include('Axioms/SET007/SET007+247.ax').
include('Axioms/SET007/SET007+248.ax').
include('Axioms/SET007/SET007+252.ax').
include('Axioms/SET007/SET007+255.ax').
include('Axioms/SET007/SET007+295.ax').
include('Axioms/SET007/SET007+312.ax').
include('Axioms/SET007/SET007+335.ax').
include('Axioms/SET007/SET007+375.ax').
include('Axioms/SET007/SET007+432.ax').
%------------------------------------------------------------------------------
fof(dt_k1_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( v1_funct_1(k1_latsubgr(A))
        & v1_funct_2(k1_latsubgr(A),k1_group_3(A),k1_zfmisc_1(u1_struct_0(A)))
        & m2_relset_1(k1_latsubgr(A),k1_group_3(A),k1_zfmisc_1(u1_struct_0(A))) ) ) ).

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

fof(dt_k3_latsubgr,axiom,
    ! [A,B,C] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & ~ v3_struct_0(B)
        & v3_group_1(B)
        & v4_group_1(B)
        & l1_group_1(B)
        & v1_funct_1(C)
        & v1_funct_2(C,u1_struct_0(A),u1_struct_0(B))
        & m1_relset_1(C,u1_struct_0(A),u1_struct_0(B)) )
     => ( v1_funct_1(k3_latsubgr(A,B,C))
        & v1_funct_2(k3_latsubgr(A,B,C),u1_struct_0(k11_group_4(A)),u1_struct_0(k11_group_4(B)))
        & m2_relset_1(k3_latsubgr(A,B,C),u1_struct_0(k11_group_4(A)),u1_struct_0(k11_group_4(B))) ) ) ).

fof(t1_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ! [C] :
              ( m1_group_2(C,A)
             => u1_struct_0(k9_group_2(A,B,C)) = k3_xboole_0(u1_struct_0(B),u1_struct_0(C)) ) ) ) ).

fof(t2_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( r2_hidden(B,k1_group_3(A))
        <=> ? [C] :
              ( v1_group_1(C)
              & m1_group_2(C,A)
              & B = C ) ) ) ).

fof(t3_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,k1_zfmisc_1(u1_struct_0(A)))
         => ! [C] :
              ( ( v1_group_1(C)
                & m1_group_2(C,A) )
             => ( B = u1_struct_0(C)
               => r1_group_2(A,k5_group_4(A,B),C) ) ) ) ) ).

fof(t4_latsubgr,axiom,
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
                  ( m1_subset_1(D,k1_zfmisc_1(u1_struct_0(A)))
                 => ( D = k2_xboole_0(u1_struct_0(B),u1_struct_0(C))
                   => r1_group_2(A,k8_group_4(A,B,C),k5_group_4(A,D)) ) ) ) ) ) ).

fof(t5_latsubgr,axiom,
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
                  ( m1_subset_1(D,u1_struct_0(A))
                 => ( ( r1_rlvect_1(B,D)
                      | r1_rlvect_1(C,D) )
                   => r1_rlvect_1(k8_group_4(A,B,C),D) ) ) ) ) ) ).

fof(t6_latsubgr,axiom,
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

fof(t7_latsubgr,axiom,
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
                  ( m1_group_2(D,B)
                 => ? [E] :
                      ( v1_group_1(E)
                      & m1_group_2(E,A)
                      & u1_struct_0(E) = k3_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(D)) ) ) ) ) ) ).

fof(t8_latsubgr,axiom,
    $true ).

fof(t9_latsubgr,axiom,
    $true ).

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

%------------------------------------------------------------------------------
