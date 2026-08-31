%------------------------------------------------------------------------------
% File     : GRP618+2 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Group of Inner Automorphisms T01
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Kor96] Kornilowicz (1996), On the Group of Inner Automorphism
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t1_autgroup [Urb08]

% Status   : Theorem
% Rating   : 0.52 v9.3.0, 0.61 v9.1.0, 0.67 v8.2.0, 0.69 v8.1.0, 0.78 v7.5.0, 0.81 v7.4.0, 0.73 v7.3.0, 0.76 v7.2.0, 0.72 v7.1.0, 0.65 v7.0.0, 0.77 v6.4.0, 0.73 v6.3.0, 0.71 v6.2.0, 0.84 v6.1.0, 0.87 v6.0.0, 0.83 v5.5.0, 0.85 v5.4.0, 0.86 v5.3.0, 0.89 v5.2.0, 0.80 v5.1.0, 0.81 v5.0.0, 0.79 v4.1.0, 0.83 v3.7.0, 0.90 v3.5.0, 0.95 v3.4.0
% Syntax   : Number of formulae    : 3809 ( 965 unt;   0 def)
%            Number of atoms       : 19251 (2727 equ)
%            Maximal formula atoms :   49 (   5 avg)
%            Number of connectives : 17575 (2133   ~; 132   |;8478   &)
%                                         ( 623 <=>;6209  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   26 (   6 avg)
%            Maximal term depth    :    6 (   1 avg)
%            Number of predicates  :  246 ( 244 usr;   1 prp; 0-4 aty)
%            Number of functors    :  625 ( 625 usr; 245 con; 0-8 aty)
%            Number of variables   : 8407 (7953   !; 454   ?)
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

fof(t1_autgroup,conjecture,
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

%------------------------------------------------------------------------------
