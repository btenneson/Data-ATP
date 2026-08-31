%------------------------------------------------------------------------------
% File     : GRP653+3 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Lattice of Subgroups of a Group T38
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Gan96] Ganczarski (1996), On the Lattice of Subgroups of a Gr
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t38_latsubgr [Urb08]

% Status   : Theorem
% Rating   : 0.74 v9.3.0, 0.76 v9.1.0, 0.82 v9.0.0, 0.83 v8.2.0, 0.89 v8.1.0, 0.92 v7.5.0, 0.94 v7.4.0, 0.97 v7.1.0, 0.91 v7.0.0, 0.90 v6.4.0, 0.88 v6.2.0, 0.92 v6.1.0, 0.97 v6.0.0, 0.91 v5.5.0, 0.93 v5.4.0, 0.96 v5.2.0, 0.95 v5.0.0, 1.00 v3.4.0
% Syntax   : Number of formulae    : 14004 (2750 unt;   0 def)
%            Number of atoms       : 87950 (9833 equ)
%            Maximal formula atoms :   62 (   6 avg)
%            Number of connectives : 85063 (11117   ~; 468   |;42390   &)
%                                         (2409 <=>;28679  =>;   0  <=;   0 <~>)
%            Maximal formula depth :   36 (   7 avg)
%            Maximal term depth    :    7 (   1 avg)
%            Number of predicates  :  805 ( 803 usr;   2 prp; 0-6 aty)
%            Number of functors    : 2049 (2049 usr; 527 con; 0-10 aty)
%            Number of variables   : 35067 (33382   !;1685   ?)
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
include('Axioms/SET007/SET007+394.ax').
include('Axioms/SET007/SET007+395.ax').
include('Axioms/SET007/SET007+396.ax').
include('Axioms/SET007/SET007+399.ax').
include('Axioms/SET007/SET007+401.ax').
include('Axioms/SET007/SET007+405.ax').
include('Axioms/SET007/SET007+406.ax').
include('Axioms/SET007/SET007+407.ax').
include('Axioms/SET007/SET007+411.ax').
include('Axioms/SET007/SET007+412.ax').
include('Axioms/SET007/SET007+426.ax').
include('Axioms/SET007/SET007+427.ax').
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

fof(t10_latsubgr,axiom,
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

fof(t11_latsubgr,axiom,
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
                 => ! [E] :
                      ( m1_group_2(E,B)
                     => ! [F] :
                          ( m1_group_2(F,A)
                         => ! [G] :
                              ( m1_group_2(G,A)
                             => ( ( u1_struct_0(F) = k3_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(D))
                                  & u1_struct_0(G) = k3_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(E))
                                  & m1_group_6(D,B,E) )
                               => m1_group_6(F,A,G) ) ) ) ) ) ) ) ) ).

fof(t12_latsubgr,axiom,
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
                & m2_relset_1(C,u1_struct_0(A),u1_struct_0(B)) )
             => ! [D] :
                  ( m1_subset_1(D,k1_zfmisc_1(u1_struct_0(A)))
                 => r1_tarski(k2_funct_2(u1_struct_0(A),u1_struct_0(B),C,D),k2_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(k5_group_4(A,D)))) ) ) ) ) ).

fof(t13_latsubgr,axiom,
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
              ( m1_group_2(C,A)
             => ! [D] :
                  ( m1_group_2(D,A)
                 => ! [E] :
                      ( ( v1_funct_1(E)
                        & v1_funct_2(E,u1_struct_0(A),u1_struct_0(B))
                        & m2_relset_1(E,u1_struct_0(A),u1_struct_0(B)) )
                     => ! [F] :
                          ( m1_subset_1(F,k1_zfmisc_1(u1_struct_0(A)))
                         => ( F = k2_xboole_0(u1_struct_0(C),u1_struct_0(D))
                           => k2_funct_2(u1_struct_0(A),u1_struct_0(B),E,u1_struct_0(k8_group_4(A,C,D))) = k2_funct_2(u1_struct_0(A),u1_struct_0(B),E,u1_struct_0(k5_group_4(A,F))) ) ) ) ) ) ) ) ).

fof(t14_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,k1_zfmisc_1(u1_struct_0(A)))
         => ( B = k18_group_2(u1_struct_0(A),k2_group_1(A))
           => r1_group_2(A,k5_group_4(A,B),k5_group_2(A)) ) ) ) ).

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

fof(t15_latsubgr,axiom,
    $true ).

fof(t16_latsubgr,axiom,
    $true ).

fof(t17_latsubgr,axiom,
    $true ).

fof(t18_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(A))
             => ( r2_hidden(C,k1_funct_1(k1_latsubgr(A),B))
              <=> r1_rlvect_1(B,C) ) ) ) ) ).

fof(t19_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => r2_hidden(k2_group_1(A),k1_funct_1(k1_latsubgr(A),B)) ) ) ).

fof(t20_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => k1_funct_1(k1_latsubgr(A),B) != k1_xboole_0 ) ) ).

fof(t21_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(A))
             => ! [D] :
                  ( m1_subset_1(D,u1_struct_0(A))
                 => ( ( r2_hidden(C,k1_funct_1(k1_latsubgr(A),B))
                      & r2_hidden(D,k1_funct_1(k1_latsubgr(A),B)) )
                   => r2_hidden(k1_group_1(A,C,D),k1_funct_1(k1_latsubgr(A),B)) ) ) ) ) ) ).

fof(t22_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & m1_group_2(B,A) )
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(A))
             => ( r2_hidden(C,k1_funct_1(k1_latsubgr(A),B))
               => r2_hidden(k3_group_1(A,C),k1_funct_1(k1_latsubgr(A),B)) ) ) ) ) ).

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

fof(t24_latsubgr,axiom,
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

fof(t25_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( ~ v1_xboole_0(B)
            & m1_subset_1(B,k1_zfmisc_1(k1_group_3(A))) )
         => ( r2_hidden(k5_group_2(A),B)
           => r1_group_2(A,k2_latsubgr(A,B),k5_group_2(A)) ) ) ) ).

fof(t26_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,k1_group_3(A))
         => ! [C] :
              ( ( ~ v1_xboole_0(C)
                & m1_subset_1(C,k1_zfmisc_1(k1_group_3(A))) )
             => ( C = k18_group_2(k1_group_3(A),B)
               => k2_latsubgr(A,C) = B ) ) ) ) ).

fof(t27_latsubgr,axiom,
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
                       => k3_lattices(k11_group_4(A),D,E) = k8_group_4(A,B,C) ) ) ) ) ) ) ).

fof(t28_latsubgr,axiom,
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
                       => k4_lattices(k11_group_4(A),D,E) = k9_group_2(A,B,C) ) ) ) ) ) ) ).

fof(t29_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(k11_group_4(A)))
         => ! [C] :
              ( m1_group_2(C,A)
             => ( B = C
               => ( v1_group_1(C)
                  & m1_group_2(C,A) ) ) ) ) ) ).

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

fof(t31_latsubgr,axiom,
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
                        <=> m1_group_6(B,A,C) ) ) ) ) ) ) ) ).

fof(t32_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => v4_lattice3(k11_group_4(A)) ) ).

fof(d3_latsubgr,axiom,
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
                & m2_relset_1(C,u1_struct_0(A),u1_struct_0(B)) )
             => ! [D] :
                  ( ( v1_funct_1(D)
                    & v1_funct_2(D,u1_struct_0(k11_group_4(A)),u1_struct_0(k11_group_4(B)))
                    & m2_relset_1(D,u1_struct_0(k11_group_4(A)),u1_struct_0(k11_group_4(B))) )
                 => ( D = k3_latsubgr(A,B,C)
                  <=> ! [E] :
                        ( ( v1_group_1(E)
                          & m1_group_2(E,A) )
                       => ! [F] :
                            ( m1_subset_1(F,k1_zfmisc_1(u1_struct_0(B)))
                           => ( F = k2_funct_2(u1_struct_0(A),u1_struct_0(B),C,u1_struct_0(E))
                             => k1_funct_1(D,E) = k5_group_4(B,F) ) ) ) ) ) ) ) ) ).

fof(t33_latsubgr,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => k3_latsubgr(A,A,k6_partfun1(u1_struct_0(A))) = k6_partfun1(u1_struct_0(k11_group_4(A))) ) ).

fof(t34_latsubgr,axiom,
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
             => ( v2_funct_1(C)
               => v2_funct_1(k3_latsubgr(A,B,C)) ) ) ) ) ).

fof(t35_latsubgr,axiom,
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
             => k1_funct_1(k3_latsubgr(A,B,C),k5_group_2(A)) = k5_group_2(B) ) ) ) ).

fof(t36_latsubgr,axiom,
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
             => ( v2_funct_1(C)
               => m3_vectsp_8(k3_latsubgr(A,B,C),k11_group_4(A),k11_group_4(B)) ) ) ) ) ).

fof(t37_latsubgr,axiom,
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
             => m4_vectsp_8(k3_latsubgr(A,B,C),k11_group_4(A),k11_group_4(B)) ) ) ) ).

fof(t38_latsubgr,conjecture,
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
             => ( v2_funct_1(C)
               => m1_lattice4(k3_latsubgr(A,B,C),k11_group_4(A),k11_group_4(B)) ) ) ) ) ).

%------------------------------------------------------------------------------
