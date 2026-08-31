%------------------------------------------------------------------------------
% File     : GRP627+3 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Group of Inner Automorphisms T18
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Kor96] Kornilowicz (1996), On the Group of Inner Automorphism
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t18_autgroup [Urb08]

% Status   : Theorem
% Rating   : 1.00 v3.4.0
% Syntax   : Number of formulae    : 12897 (2694 unt;   0 def)
%            Number of atoms       : 78945 (9011 equ)
%            Maximal formula atoms :   52 (   6 avg)
%            Number of connectives : 75590 (9542   ~; 436   |;37666   &)
%                                         (2139 <=>;25807  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   36 (   7 avg)
%            Maximal term depth    :    7 (   1 avg)
%            Number of predicates  :  722 ( 720 usr;   2 prp; 0-6 aty)
%            Number of functors    : 1842 (1842 usr; 498 con; 0-10 aty)
%            Number of variables   : 31825 (30319   !;1506   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Chainy small version: includes all preceding MML articles that
%            are included in any Bushy version.
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
include('Axioms/SET007/SET007+15.ax').
include('Axioms/SET007/SET007+16.ax').
include('Axioms/SET007/SET007+17.ax').
include('Axioms/SET007/SET007+18.ax').
include('Axioms/SET007/SET007+19.ax').
include('Axioms/SET007/SET007+20.ax').
include('Axioms/SET007/SET007+21.ax').
include('Axioms/SET007/SET007+22.ax').
include('Axioms/SET007/SET007+23.ax').
include('Axioms/SET007/SET007+24.ax').
include('Axioms/SET007/SET007+25.ax').
include('Axioms/SET007/SET007+26.ax').
include('Axioms/SET007/SET007+31.ax').
include('Axioms/SET007/SET007+32.ax').
include('Axioms/SET007/SET007+33.ax').
include('Axioms/SET007/SET007+34.ax').
include('Axioms/SET007/SET007+35.ax').
include('Axioms/SET007/SET007+40.ax').
include('Axioms/SET007/SET007+48.ax').
include('Axioms/SET007/SET007+50.ax').
include('Axioms/SET007/SET007+51.ax').
include('Axioms/SET007/SET007+54.ax').
include('Axioms/SET007/SET007+55.ax').
include('Axioms/SET007/SET007+59.ax').
include('Axioms/SET007/SET007+60.ax').
include('Axioms/SET007/SET007+61.ax').
include('Axioms/SET007/SET007+64.ax').
include('Axioms/SET007/SET007+66.ax').
include('Axioms/SET007/SET007+67.ax').
include('Axioms/SET007/SET007+68.ax').
include('Axioms/SET007/SET007+71.ax').
include('Axioms/SET007/SET007+75.ax').
include('Axioms/SET007/SET007+76.ax').
include('Axioms/SET007/SET007+77.ax').
include('Axioms/SET007/SET007+79.ax').
include('Axioms/SET007/SET007+80.ax').
include('Axioms/SET007/SET007+86.ax').
include('Axioms/SET007/SET007+91.ax').
include('Axioms/SET007/SET007+117.ax').
include('Axioms/SET007/SET007+125.ax').
include('Axioms/SET007/SET007+126.ax').
include('Axioms/SET007/SET007+148.ax').
include('Axioms/SET007/SET007+159.ax').
include('Axioms/SET007/SET007+165.ax').
include('Axioms/SET007/SET007+170.ax').
include('Axioms/SET007/SET007+182.ax').
include('Axioms/SET007/SET007+186.ax').
include('Axioms/SET007/SET007+188.ax').
include('Axioms/SET007/SET007+190.ax').
include('Axioms/SET007/SET007+200.ax').
include('Axioms/SET007/SET007+202.ax').
include('Axioms/SET007/SET007+205.ax').
include('Axioms/SET007/SET007+206.ax').
include('Axioms/SET007/SET007+207.ax').
include('Axioms/SET007/SET007+209.ax').
include('Axioms/SET007/SET007+210.ax').
include('Axioms/SET007/SET007+211.ax').
include('Axioms/SET007/SET007+212.ax').
include('Axioms/SET007/SET007+213.ax').
include('Axioms/SET007/SET007+217.ax').
include('Axioms/SET007/SET007+218.ax').
include('Axioms/SET007/SET007+223.ax').
include('Axioms/SET007/SET007+224.ax').
include('Axioms/SET007/SET007+225.ax').
include('Axioms/SET007/SET007+227.ax').
include('Axioms/SET007/SET007+237.ax').
include('Axioms/SET007/SET007+241.ax').
include('Axioms/SET007/SET007+242.ax').
include('Axioms/SET007/SET007+246.ax').
include('Axioms/SET007/SET007+247.ax').
include('Axioms/SET007/SET007+248.ax').
include('Axioms/SET007/SET007+252.ax').
include('Axioms/SET007/SET007+253.ax').
include('Axioms/SET007/SET007+255.ax').
include('Axioms/SET007/SET007+256.ax').
include('Axioms/SET007/SET007+276.ax').
include('Axioms/SET007/SET007+278.ax').
include('Axioms/SET007/SET007+279.ax').
include('Axioms/SET007/SET007+280.ax').
include('Axioms/SET007/SET007+281.ax').
include('Axioms/SET007/SET007+293.ax').
include('Axioms/SET007/SET007+295.ax').
include('Axioms/SET007/SET007+297.ax').
include('Axioms/SET007/SET007+298.ax').
include('Axioms/SET007/SET007+299.ax').
include('Axioms/SET007/SET007+301.ax').
include('Axioms/SET007/SET007+308.ax').
include('Axioms/SET007/SET007+309.ax').
include('Axioms/SET007/SET007+311.ax').
include('Axioms/SET007/SET007+312.ax').
include('Axioms/SET007/SET007+317.ax').
include('Axioms/SET007/SET007+321.ax').
include('Axioms/SET007/SET007+322.ax').
include('Axioms/SET007/SET007+327.ax').
include('Axioms/SET007/SET007+335.ax').
include('Axioms/SET007/SET007+338.ax').
include('Axioms/SET007/SET007+339.ax').
include('Axioms/SET007/SET007+354.ax').
include('Axioms/SET007/SET007+363.ax').
include('Axioms/SET007/SET007+365.ax').
include('Axioms/SET007/SET007+370.ax').
include('Axioms/SET007/SET007+375.ax').
include('Axioms/SET007/SET007+377.ax').
include('Axioms/SET007/SET007+384.ax').
include('Axioms/SET007/SET007+387.ax').
include('Axioms/SET007/SET007+388.ax').
include('Axioms/SET007/SET007+393.ax').
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

fof(t8_autgroup,axiom,
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

fof(d2_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_funct_1(B)
            & v1_funct_2(B,k2_zfmisc_1(k1_autgroup(A),k1_autgroup(A)),k1_autgroup(A))
            & m2_relset_1(B,k2_zfmisc_1(k1_autgroup(A),k1_autgroup(A)),k1_autgroup(A)) )
         => ( B = k2_autgroup(A)
          <=> ! [C] :
                ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
               => ! [D] :
                    ( m2_fraenkel(D,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
                   => k2_binop_1(k1_autgroup(A),k1_autgroup(A),k1_autgroup(A),B,C,D) = k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),D,C) ) ) ) ) ) ).

fof(d3_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => k3_autgroup(A) = g1_group_1(k1_autgroup(A),k2_autgroup(A)) ) ).

fof(t9_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(k3_autgroup(A)))
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(k3_autgroup(A)))
             => ! [D] :
                  ( m2_fraenkel(D,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
                 => ! [E] :
                      ( m2_fraenkel(E,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
                     => ( ( B = D
                          & C = E )
                       => k1_group_1(k3_autgroup(A),B,C) = k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),E,D) ) ) ) ) ) ) ).

fof(t10_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => k6_partfun1(u1_struct_0(A)) = k2_group_1(k3_autgroup(A)) ) ).

fof(t11_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A))
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(k3_autgroup(A)))
             => ( B = C
               => k2_funct_1(B) = k3_group_1(k3_autgroup(A),C) ) ) ) ) ).

fof(d4_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_fraenkel(B,u1_struct_0(A),u1_struct_0(A))
         => ( B = k4_autgroup(A)
          <=> ! [C] :
                ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),k1_fraenkel(u1_struct_0(A),u1_struct_0(A)))
               => ( r2_hidden(C,B)
                <=> ? [D] :
                      ( m1_subset_1(D,u1_struct_0(A))
                      & ! [E] :
                          ( m1_subset_1(E,u1_struct_0(A))
                         => k8_funct_2(u1_struct_0(A),u1_struct_0(A),C,E) = k2_group_3(A,E,D) ) ) ) ) ) ) ) ).

fof(t12_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => r1_tarski(k4_autgroup(A),k1_fraenkel(u1_struct_0(A),u1_struct_0(A))) ) ).

fof(t13_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
         => m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k1_autgroup(A)) ) ) ).

fof(t14_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => r1_tarski(k4_autgroup(A),k1_autgroup(A)) ) ).

fof(t15_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
         => ! [C] :
              ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
             => k1_binop_1(k2_autgroup(A),B,C) = k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),C,B) ) ) ) ).

fof(t16_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => m2_fraenkel(k6_partfun1(u1_struct_0(A)),u1_struct_0(A),u1_struct_0(A),k4_autgroup(A)) ) ).

fof(t17_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
         => m2_fraenkel(k2_funct_1(B),u1_struct_0(A),u1_struct_0(A),k4_autgroup(A)) ) ) ).

fof(t18_autgroup,conjecture,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
         => ! [C] :
              ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
             => m2_fraenkel(k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),C,B),u1_struct_0(A),u1_struct_0(A),k4_autgroup(A)) ) ) ) ).

%------------------------------------------------------------------------------
