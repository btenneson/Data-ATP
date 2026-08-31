%------------------------------------------------------------------------------
% File     : GRP621+2 : TPTP v9.3.1. Released v3.4.0.
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
% Rating   : 0.96 v9.3.0, 1.00 v3.4.0
% Syntax   : Number of formulae    : 3818 ( 966 unt;   0 def)
%            Number of atoms       : 19327 (2730 equ)
%            Maximal formula atoms :   49 (   5 avg)
%            Number of connectives : 17650 (2141   ~; 132   |;8525   &)
%                                         ( 626 <=>;6226  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   26 (   6 avg)
%            Maximal term depth    :    6 (   1 avg)
%            Number of predicates  :  246 ( 244 usr;   1 prp; 0-4 aty)
%            Number of functors    :  625 ( 625 usr; 245 con; 0-8 aty)
%            Number of variables   : 8424 (7970   !; 454   ?)
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
include('Axioms/SET007/SET007+6.ax').
include('Axioms/SET007/SET007+7.ax').
include('Axioms/SET007/SET007+9.ax').
include('Axioms/SET007/SET007+10.ax').
include('Axioms/SET007/SET007+11.ax').
include('Axioms/SET007/SET007+13.ax').
include('Axioms/SET007/SET007+14.ax').
include('Axioms/SET007/SET007+16.ax').
include('Axioms/SET007/SET007+17.ax').
include('Axioms/SET007/SET007+20.ax').
include('Axioms/SET007/SET007+23.ax').
include('Axioms/SET007/SET007+24.ax').
include('Axioms/SET007/SET007+26.ax').
include('Axioms/SET007/SET007+31.ax').
include('Axioms/SET007/SET007+32.ax').
include('Axioms/SET007/SET007+34.ax').
include('Axioms/SET007/SET007+35.ax').
include('Axioms/SET007/SET007+40.ax').
include('Axioms/SET007/SET007+48.ax').
include('Axioms/SET007/SET007+54.ax').
include('Axioms/SET007/SET007+55.ax').
include('Axioms/SET007/SET007+117.ax').
include('Axioms/SET007/SET007+200.ax').
include('Axioms/SET007/SET007+210.ax').
include('Axioms/SET007/SET007+212.ax').
include('Axioms/SET007/SET007+213.ax').
include('Axioms/SET007/SET007+223.ax').
include('Axioms/SET007/SET007+246.ax').
include('Axioms/SET007/SET007+252.ax').
include('Axioms/SET007/SET007+298.ax').
include('Axioms/SET007/SET007+312.ax').
include('Axioms/SET007/SET007+338.ax').
%------------------------------------------------------------------------------
fof(dt_k1_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => m1_fraenkel(k1_autgroup(A),u1_struct_0(A),u1_struct_0(A)) ) ).

fof(dt_k2_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( v1_funct_1(k2_autgroup(A))
        & v1_funct_2(k2_autgroup(A),k2_zfmisc_1(k1_autgroup(A),k1_autgroup(A)),k1_autgroup(A))
        & m2_relset_1(k2_autgroup(A),k2_zfmisc_1(k1_autgroup(A),k1_autgroup(A)),k1_autgroup(A)) ) ) ).

fof(dt_k3_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( ~ v3_struct_0(k3_autgroup(A))
        & v1_group_1(k3_autgroup(A))
        & v3_group_1(k3_autgroup(A))
        & v4_group_1(k3_autgroup(A))
        & l1_group_1(k3_autgroup(A)) ) ) ).

fof(dt_k4_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => m1_fraenkel(k4_autgroup(A),u1_struct_0(A),u1_struct_0(A)) ) ).

fof(dt_k5_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( v1_group_1(k5_autgroup(A))
        & v1_group_3(k5_autgroup(A),k3_autgroup(A))
        & m1_group_2(k5_autgroup(A),k3_autgroup(A)) ) ) ).

fof(dt_k6_autgroup,axiom,
    ! [A,B] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A)
        & m1_subset_1(B,u1_struct_0(A)) )
     => m2_fraenkel(k6_autgroup(A,B),u1_struct_0(A),u1_struct_0(A),k4_autgroup(A)) ) ).

fof(l1_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ( ! [C] :
                ( m1_subset_1(C,u1_struct_0(A))
               => ! [D] :
                    ( m1_subset_1(D,u1_struct_0(A))
                   => ( m1_subset_1(D,u1_struct_0(B))
                     => r1_rlvect_1(B,k2_group_3(A,D,C)) ) ) )
           => v1_group_3(B,A) ) ) ) ).

fof(l2_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ( v1_group_3(B,A)
           => ! [C] :
                ( m1_subset_1(C,u1_struct_0(A))
               => ! [D] :
                    ( m1_subset_1(D,u1_struct_0(A))
                   => ( m1_subset_1(D,u1_struct_0(B))
                     => r1_rlvect_1(B,k2_group_3(A,D,C)) ) ) ) ) ) ) ).

fof(t1_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_group_2(B,A)
         => ( ! [C] :
                ( m1_subset_1(C,u1_struct_0(A))
               => ! [D] :
                    ( m1_subset_1(D,u1_struct_0(A))
                   => ( m1_subset_1(D,u1_struct_0(B))
                     => r1_rlvect_1(B,k2_group_3(A,D,C)) ) ) )
          <=> v1_group_3(B,A) ) ) ) ).

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

fof(t2_autgroup,axiom,
    $true ).

fof(t3_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => r1_tarski(k1_autgroup(A),k1_fraenkel(u1_struct_0(A),u1_struct_0(A))) ) ).

fof(t4_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => m2_fraenkel(k6_partfun1(u1_struct_0(A)),u1_struct_0(A),u1_struct_0(A),k1_autgroup(A)) ) ).

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

fof(l9_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
         => ( k1_relat_1(B) = k2_relat_1(B)
            & k1_relat_1(B) = u1_struct_0(A) ) ) ) ).

fof(t6_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
         => ( v1_funct_1(k2_funct_1(B))
            & v1_funct_2(k2_funct_1(B),u1_struct_0(A),u1_struct_0(A))
            & v1_group_6(k2_funct_1(B),A,A)
            & m2_relset_1(k2_funct_1(B),u1_struct_0(A),u1_struct_0(A)) ) ) ) ).

fof(t7_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
         => m2_fraenkel(k2_funct_1(B),u1_struct_0(A),u1_struct_0(A),k1_autgroup(A)) ) ) ).

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

%------------------------------------------------------------------------------
