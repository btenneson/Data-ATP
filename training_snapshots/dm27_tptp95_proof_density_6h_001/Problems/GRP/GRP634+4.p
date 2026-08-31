%------------------------------------------------------------------------------
% File     : GRP634+4 : TPTP v9.3.1. Released v3.4.0.
% Domain   : Group Theory
% Problem  : On the Group of Inner Automorphisms T32
% Version  : [Urb08] axioms : Especial.
% English  :

% Refs     : [Kor96] Kornilowicz (1996), On the Group of Inner Automorphism
%          : [Urb07] Urban (2007), MPTP 0.2: Design, Implementation, and In
%          : [Urb08] Urban (2006), Email to G. Sutcliffe
% Source   : [Urb08]
% Names    : t32_autgroup [Urb08]

% Status   : Theorem
% Rating   : 0.91 v9.3.0, 0.97 v8.1.0, 0.94 v7.5.0, 1.00 v6.0.0, 0.96 v5.5.0, 1.00 v3.4.0
% Syntax   : Number of formulae    : 33431 (5854 unt;   0 def)
%            Number of atoms       : 234204 (27880 equ)
%            Maximal formula atoms :  208 (   7 avg)
%            Number of connectives : 234313 (33540   ~;2826   |;112153   &)
%                                         (5392 <=>;80402  =>;   0  <=;   0 <~>)
%            Maximal formula depth :  150 (   8 avg)
%            Maximal term depth    :   12 (   1 avg)
%            Number of predicates  : 1732 (1730 usr;   3 prp; 0-8 aty)
%            Number of functors    : 4481 (4481 usr;1009 con; 0-10 aty)
%            Number of variables   : 91729 (87354   !;4375   ?)
% SPC      : FOF_THM_RFO_SEQ

% Comments : Chainy large version: includes all preceding MML articles.
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
include('Axioms/SET007/SET007+12.ax').
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
include('Axioms/SET007/SET007+27.ax').
include('Axioms/SET007/SET007+28.ax').
include('Axioms/SET007/SET007+29.ax').
include('Axioms/SET007/SET007+30.ax').
include('Axioms/SET007/SET007+31.ax').
include('Axioms/SET007/SET007+32.ax').
include('Axioms/SET007/SET007+33.ax').
include('Axioms/SET007/SET007+34.ax').
include('Axioms/SET007/SET007+35.ax').
include('Axioms/SET007/SET007+36.ax').
include('Axioms/SET007/SET007+37.ax').
include('Axioms/SET007/SET007+38.ax').
include('Axioms/SET007/SET007+39.ax').
include('Axioms/SET007/SET007+40.ax').
include('Axioms/SET007/SET007+41.ax').
include('Axioms/SET007/SET007+42.ax').
include('Axioms/SET007/SET007+43.ax').
include('Axioms/SET007/SET007+44.ax').
include('Axioms/SET007/SET007+45.ax').
include('Axioms/SET007/SET007+46.ax').
include('Axioms/SET007/SET007+47.ax').
include('Axioms/SET007/SET007+48.ax').
include('Axioms/SET007/SET007+49.ax').
include('Axioms/SET007/SET007+50.ax').
include('Axioms/SET007/SET007+51.ax').
include('Axioms/SET007/SET007+52.ax').
include('Axioms/SET007/SET007+53.ax').
include('Axioms/SET007/SET007+54.ax').
include('Axioms/SET007/SET007+55.ax').
include('Axioms/SET007/SET007+56.ax').
include('Axioms/SET007/SET007+57.ax').
include('Axioms/SET007/SET007+58.ax').
include('Axioms/SET007/SET007+59.ax').
include('Axioms/SET007/SET007+60.ax').
include('Axioms/SET007/SET007+61.ax').
include('Axioms/SET007/SET007+62.ax').
include('Axioms/SET007/SET007+63.ax').
include('Axioms/SET007/SET007+64.ax').
include('Axioms/SET007/SET007+65.ax').
include('Axioms/SET007/SET007+66.ax').
include('Axioms/SET007/SET007+67.ax').
include('Axioms/SET007/SET007+68.ax').
include('Axioms/SET007/SET007+69.ax').
include('Axioms/SET007/SET007+70.ax').
include('Axioms/SET007/SET007+71.ax').
include('Axioms/SET007/SET007+72.ax').
include('Axioms/SET007/SET007+73.ax').
include('Axioms/SET007/SET007+74.ax').
include('Axioms/SET007/SET007+75.ax').
include('Axioms/SET007/SET007+76.ax').
include('Axioms/SET007/SET007+77.ax').
include('Axioms/SET007/SET007+78.ax').
include('Axioms/SET007/SET007+79.ax').
include('Axioms/SET007/SET007+80.ax').
include('Axioms/SET007/SET007+81.ax').
include('Axioms/SET007/SET007+82.ax').
include('Axioms/SET007/SET007+83.ax').
include('Axioms/SET007/SET007+84.ax').
include('Axioms/SET007/SET007+85.ax').
include('Axioms/SET007/SET007+86.ax').
include('Axioms/SET007/SET007+87.ax').
include('Axioms/SET007/SET007+88.ax').
include('Axioms/SET007/SET007+89.ax').
include('Axioms/SET007/SET007+90.ax').
include('Axioms/SET007/SET007+91.ax').
include('Axioms/SET007/SET007+92.ax').
include('Axioms/SET007/SET007+93.ax').
include('Axioms/SET007/SET007+94.ax').
include('Axioms/SET007/SET007+95.ax').
include('Axioms/SET007/SET007+96.ax').
include('Axioms/SET007/SET007+97.ax').
include('Axioms/SET007/SET007+98.ax').
include('Axioms/SET007/SET007+99.ax').
include('Axioms/SET007/SET007+100.ax').
include('Axioms/SET007/SET007+101.ax').
include('Axioms/SET007/SET007+102.ax').
include('Axioms/SET007/SET007+103.ax').
include('Axioms/SET007/SET007+104.ax').
include('Axioms/SET007/SET007+105.ax').
include('Axioms/SET007/SET007+106.ax').
include('Axioms/SET007/SET007+107.ax').
include('Axioms/SET007/SET007+108.ax').
include('Axioms/SET007/SET007+109.ax').
include('Axioms/SET007/SET007+110.ax').
include('Axioms/SET007/SET007+111.ax').
include('Axioms/SET007/SET007+112.ax').
include('Axioms/SET007/SET007+113.ax').
include('Axioms/SET007/SET007+114.ax').
include('Axioms/SET007/SET007+115.ax').
include('Axioms/SET007/SET007+116.ax').
include('Axioms/SET007/SET007+117.ax').
include('Axioms/SET007/SET007+118.ax').
include('Axioms/SET007/SET007+119.ax').
include('Axioms/SET007/SET007+120.ax').
include('Axioms/SET007/SET007+121.ax').
include('Axioms/SET007/SET007+122.ax').
include('Axioms/SET007/SET007+123.ax').
include('Axioms/SET007/SET007+124.ax').
include('Axioms/SET007/SET007+125.ax').
include('Axioms/SET007/SET007+126.ax').
include('Axioms/SET007/SET007+127.ax').
include('Axioms/SET007/SET007+128.ax').
include('Axioms/SET007/SET007+129.ax').
include('Axioms/SET007/SET007+130.ax').
include('Axioms/SET007/SET007+131.ax').
include('Axioms/SET007/SET007+132.ax').
include('Axioms/SET007/SET007+133.ax').
include('Axioms/SET007/SET007+134.ax').
include('Axioms/SET007/SET007+135.ax').
include('Axioms/SET007/SET007+136.ax').
include('Axioms/SET007/SET007+137.ax').
include('Axioms/SET007/SET007+138.ax').
include('Axioms/SET007/SET007+139.ax').
include('Axioms/SET007/SET007+140.ax').
include('Axioms/SET007/SET007+141.ax').
include('Axioms/SET007/SET007+142.ax').
include('Axioms/SET007/SET007+143.ax').
include('Axioms/SET007/SET007+144.ax').
include('Axioms/SET007/SET007+145.ax').
include('Axioms/SET007/SET007+146.ax').
include('Axioms/SET007/SET007+147.ax').
include('Axioms/SET007/SET007+148.ax').
include('Axioms/SET007/SET007+149.ax').
include('Axioms/SET007/SET007+150.ax').
include('Axioms/SET007/SET007+151.ax').
include('Axioms/SET007/SET007+152.ax').
include('Axioms/SET007/SET007+153.ax').
include('Axioms/SET007/SET007+154.ax').
include('Axioms/SET007/SET007+155.ax').
include('Axioms/SET007/SET007+156.ax').
include('Axioms/SET007/SET007+157.ax').
include('Axioms/SET007/SET007+158.ax').
include('Axioms/SET007/SET007+159.ax').
include('Axioms/SET007/SET007+160.ax').
include('Axioms/SET007/SET007+161.ax').
include('Axioms/SET007/SET007+162.ax').
include('Axioms/SET007/SET007+163.ax').
include('Axioms/SET007/SET007+164.ax').
include('Axioms/SET007/SET007+165.ax').
include('Axioms/SET007/SET007+166.ax').
include('Axioms/SET007/SET007+167.ax').
include('Axioms/SET007/SET007+168.ax').
include('Axioms/SET007/SET007+169.ax').
include('Axioms/SET007/SET007+170.ax').
include('Axioms/SET007/SET007+171.ax').
include('Axioms/SET007/SET007+172.ax').
include('Axioms/SET007/SET007+173.ax').
include('Axioms/SET007/SET007+174.ax').
include('Axioms/SET007/SET007+175.ax').
include('Axioms/SET007/SET007+176.ax').
include('Axioms/SET007/SET007+177.ax').
include('Axioms/SET007/SET007+178.ax').
include('Axioms/SET007/SET007+179.ax').
include('Axioms/SET007/SET007+180.ax').
include('Axioms/SET007/SET007+181.ax').
include('Axioms/SET007/SET007+182.ax').
include('Axioms/SET007/SET007+183.ax').
include('Axioms/SET007/SET007+184.ax').
include('Axioms/SET007/SET007+185.ax').
include('Axioms/SET007/SET007+186.ax').
include('Axioms/SET007/SET007+187.ax').
include('Axioms/SET007/SET007+188.ax').
include('Axioms/SET007/SET007+189.ax').
include('Axioms/SET007/SET007+190.ax').
include('Axioms/SET007/SET007+191.ax').
include('Axioms/SET007/SET007+192.ax').
include('Axioms/SET007/SET007+193.ax').
include('Axioms/SET007/SET007+194.ax').
include('Axioms/SET007/SET007+195.ax').
include('Axioms/SET007/SET007+196.ax').
include('Axioms/SET007/SET007+197.ax').
include('Axioms/SET007/SET007+198.ax').
include('Axioms/SET007/SET007+199.ax').
include('Axioms/SET007/SET007+200.ax').
include('Axioms/SET007/SET007+201.ax').
include('Axioms/SET007/SET007+202.ax').
include('Axioms/SET007/SET007+203.ax').
include('Axioms/SET007/SET007+204.ax').
include('Axioms/SET007/SET007+205.ax').
include('Axioms/SET007/SET007+206.ax').
include('Axioms/SET007/SET007+207.ax').
include('Axioms/SET007/SET007+208.ax').
include('Axioms/SET007/SET007+209.ax').
include('Axioms/SET007/SET007+210.ax').
include('Axioms/SET007/SET007+211.ax').
include('Axioms/SET007/SET007+212.ax').
include('Axioms/SET007/SET007+213.ax').
include('Axioms/SET007/SET007+214.ax').
include('Axioms/SET007/SET007+215.ax').
include('Axioms/SET007/SET007+216.ax').
include('Axioms/SET007/SET007+217.ax').
include('Axioms/SET007/SET007+218.ax').
include('Axioms/SET007/SET007+219.ax').
include('Axioms/SET007/SET007+220.ax').
include('Axioms/SET007/SET007+221.ax').
include('Axioms/SET007/SET007+222.ax').
include('Axioms/SET007/SET007+223.ax').
include('Axioms/SET007/SET007+224.ax').
include('Axioms/SET007/SET007+225.ax').
include('Axioms/SET007/SET007+226.ax').
include('Axioms/SET007/SET007+227.ax').
include('Axioms/SET007/SET007+228.ax').
include('Axioms/SET007/SET007+229.ax').
include('Axioms/SET007/SET007+230.ax').
include('Axioms/SET007/SET007+231.ax').
include('Axioms/SET007/SET007+232.ax').
include('Axioms/SET007/SET007+233.ax').
include('Axioms/SET007/SET007+234.ax').
include('Axioms/SET007/SET007+235.ax').
include('Axioms/SET007/SET007+236.ax').
include('Axioms/SET007/SET007+237.ax').
include('Axioms/SET007/SET007+238.ax').
include('Axioms/SET007/SET007+239.ax').
include('Axioms/SET007/SET007+240.ax').
include('Axioms/SET007/SET007+241.ax').
include('Axioms/SET007/SET007+242.ax').
include('Axioms/SET007/SET007+243.ax').
include('Axioms/SET007/SET007+244.ax').
include('Axioms/SET007/SET007+245.ax').
include('Axioms/SET007/SET007+246.ax').
include('Axioms/SET007/SET007+247.ax').
include('Axioms/SET007/SET007+248.ax').
include('Axioms/SET007/SET007+249.ax').
include('Axioms/SET007/SET007+250.ax').
include('Axioms/SET007/SET007+251.ax').
include('Axioms/SET007/SET007+252.ax').
include('Axioms/SET007/SET007+253.ax').
include('Axioms/SET007/SET007+254.ax').
include('Axioms/SET007/SET007+255.ax').
include('Axioms/SET007/SET007+256.ax').
include('Axioms/SET007/SET007+257.ax').
include('Axioms/SET007/SET007+258.ax').
include('Axioms/SET007/SET007+259.ax').
include('Axioms/SET007/SET007+260.ax').
include('Axioms/SET007/SET007+261.ax').
include('Axioms/SET007/SET007+262.ax').
include('Axioms/SET007/SET007+263.ax').
include('Axioms/SET007/SET007+264.ax').
include('Axioms/SET007/SET007+265.ax').
include('Axioms/SET007/SET007+266.ax').
include('Axioms/SET007/SET007+267.ax').
include('Axioms/SET007/SET007+268.ax').
include('Axioms/SET007/SET007+269.ax').
include('Axioms/SET007/SET007+270.ax').
include('Axioms/SET007/SET007+271.ax').
include('Axioms/SET007/SET007+272.ax').
include('Axioms/SET007/SET007+273.ax').
include('Axioms/SET007/SET007+274.ax').
include('Axioms/SET007/SET007+275.ax').
include('Axioms/SET007/SET007+276.ax').
include('Axioms/SET007/SET007+277.ax').
include('Axioms/SET007/SET007+278.ax').
include('Axioms/SET007/SET007+279.ax').
include('Axioms/SET007/SET007+280.ax').
include('Axioms/SET007/SET007+281.ax').
include('Axioms/SET007/SET007+282.ax').
include('Axioms/SET007/SET007+283.ax').
include('Axioms/SET007/SET007+284.ax').
include('Axioms/SET007/SET007+285.ax').
include('Axioms/SET007/SET007+286.ax').
include('Axioms/SET007/SET007+287.ax').
include('Axioms/SET007/SET007+288.ax').
include('Axioms/SET007/SET007+289.ax').
include('Axioms/SET007/SET007+290.ax').
include('Axioms/SET007/SET007+291.ax').
include('Axioms/SET007/SET007+292.ax').
include('Axioms/SET007/SET007+293.ax').
include('Axioms/SET007/SET007+294.ax').
include('Axioms/SET007/SET007+295.ax').
include('Axioms/SET007/SET007+296.ax').
include('Axioms/SET007/SET007+297.ax').
include('Axioms/SET007/SET007+298.ax').
include('Axioms/SET007/SET007+299.ax').
include('Axioms/SET007/SET007+300.ax').
include('Axioms/SET007/SET007+301.ax').
include('Axioms/SET007/SET007+302.ax').
include('Axioms/SET007/SET007+303.ax').
include('Axioms/SET007/SET007+304.ax').
include('Axioms/SET007/SET007+305.ax').
include('Axioms/SET007/SET007+306.ax').
include('Axioms/SET007/SET007+307.ax').
include('Axioms/SET007/SET007+308.ax').
include('Axioms/SET007/SET007+309.ax').
include('Axioms/SET007/SET007+310.ax').
include('Axioms/SET007/SET007+311.ax').
include('Axioms/SET007/SET007+312.ax').
include('Axioms/SET007/SET007+313.ax').
include('Axioms/SET007/SET007+314.ax').
include('Axioms/SET007/SET007+315.ax').
include('Axioms/SET007/SET007+316.ax').
include('Axioms/SET007/SET007+317.ax').
include('Axioms/SET007/SET007+318.ax').
include('Axioms/SET007/SET007+319.ax').
include('Axioms/SET007/SET007+320.ax').
include('Axioms/SET007/SET007+321.ax').
include('Axioms/SET007/SET007+322.ax').
include('Axioms/SET007/SET007+323.ax').
include('Axioms/SET007/SET007+324.ax').
include('Axioms/SET007/SET007+325.ax').
include('Axioms/SET007/SET007+326.ax').
include('Axioms/SET007/SET007+327.ax').
include('Axioms/SET007/SET007+328.ax').
include('Axioms/SET007/SET007+329.ax').
include('Axioms/SET007/SET007+330.ax').
include('Axioms/SET007/SET007+331.ax').
include('Axioms/SET007/SET007+332.ax').
include('Axioms/SET007/SET007+333.ax').
include('Axioms/SET007/SET007+334.ax').
include('Axioms/SET007/SET007+335.ax').
include('Axioms/SET007/SET007+336.ax').
include('Axioms/SET007/SET007+337.ax').
include('Axioms/SET007/SET007+338.ax').
include('Axioms/SET007/SET007+339.ax').
include('Axioms/SET007/SET007+340.ax').
include('Axioms/SET007/SET007+341.ax').
include('Axioms/SET007/SET007+342.ax').
include('Axioms/SET007/SET007+343.ax').
include('Axioms/SET007/SET007+344.ax').
include('Axioms/SET007/SET007+345.ax').
include('Axioms/SET007/SET007+346.ax').
include('Axioms/SET007/SET007+347.ax').
include('Axioms/SET007/SET007+348.ax').
include('Axioms/SET007/SET007+349.ax').
include('Axioms/SET007/SET007+350.ax').
include('Axioms/SET007/SET007+351.ax').
include('Axioms/SET007/SET007+352.ax').
include('Axioms/SET007/SET007+353.ax').
include('Axioms/SET007/SET007+354.ax').
include('Axioms/SET007/SET007+355.ax').
include('Axioms/SET007/SET007+356.ax').
include('Axioms/SET007/SET007+357.ax').
include('Axioms/SET007/SET007+358.ax').
include('Axioms/SET007/SET007+359.ax').
include('Axioms/SET007/SET007+360.ax').
include('Axioms/SET007/SET007+361.ax').
include('Axioms/SET007/SET007+362.ax').
include('Axioms/SET007/SET007+363.ax').
include('Axioms/SET007/SET007+364.ax').
include('Axioms/SET007/SET007+365.ax').
include('Axioms/SET007/SET007+366.ax').
include('Axioms/SET007/SET007+367.ax').
include('Axioms/SET007/SET007+368.ax').
include('Axioms/SET007/SET007+369.ax').
include('Axioms/SET007/SET007+370.ax').
include('Axioms/SET007/SET007+371.ax').
include('Axioms/SET007/SET007+372.ax').
include('Axioms/SET007/SET007+373.ax').
include('Axioms/SET007/SET007+374.ax').
include('Axioms/SET007/SET007+375.ax').
include('Axioms/SET007/SET007+376.ax').
include('Axioms/SET007/SET007+377.ax').
include('Axioms/SET007/SET007+378.ax').
include('Axioms/SET007/SET007+379.ax').
include('Axioms/SET007/SET007+380.ax').
include('Axioms/SET007/SET007+381.ax').
include('Axioms/SET007/SET007+382.ax').
include('Axioms/SET007/SET007+383.ax').
include('Axioms/SET007/SET007+384.ax').
include('Axioms/SET007/SET007+385.ax').
include('Axioms/SET007/SET007+386.ax').
include('Axioms/SET007/SET007+387.ax').
include('Axioms/SET007/SET007+388.ax').
include('Axioms/SET007/SET007+389.ax').
include('Axioms/SET007/SET007+390.ax').
include('Axioms/SET007/SET007+391.ax').
include('Axioms/SET007/SET007+392.ax').
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

fof(t18_autgroup,axiom,
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

fof(d5_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( ( v1_group_1(B)
            & v1_group_3(B,k3_autgroup(A))
            & m1_group_2(B,k3_autgroup(A)) )
         => ( B = k5_autgroup(A)
          <=> u1_struct_0(B) = k4_autgroup(A) ) ) ) ).

fof(t19_autgroup,axiom,
    $true ).

fof(t20_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(k5_autgroup(A)))
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(k5_autgroup(A)))
             => ! [D] :
                  ( m2_fraenkel(D,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
                 => ! [E] :
                      ( m2_fraenkel(E,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
                     => ( ( B = D
                          & C = E )
                       => k1_group_1(k5_autgroup(A),B,C) = k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),E,D) ) ) ) ) ) ) ).

fof(t21_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => k6_partfun1(u1_struct_0(A)) = k2_group_1(k5_autgroup(A)) ) ).

fof(t22_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(k5_autgroup(A)))
             => ( B = C
               => k2_funct_1(B) = k3_group_1(k5_autgroup(A),C) ) ) ) ) ).

fof(d6_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => ! [C] :
              ( m2_fraenkel(C,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
             => ( C = k6_autgroup(A,B)
              <=> ! [D] :
                    ( m1_subset_1(D,u1_struct_0(A))
                   => k8_funct_2(u1_struct_0(A),u1_struct_0(A),C,D) = k2_group_3(A,D,B) ) ) ) ) ) ).

fof(t23_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => ! [C] :
              ( m1_subset_1(C,u1_struct_0(A))
             => k6_autgroup(A,k1_group_1(A,B,C)) = k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,B),k6_autgroup(A,C)) ) ) ) ).

fof(t24_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => k6_autgroup(A,k2_group_1(A)) = k6_partfun1(u1_struct_0(A)) ) ).

fof(t25_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => k8_funct_2(u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,k2_group_1(A)),B) = B ) ) ).

fof(t26_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,k3_group_1(A,B)),k6_autgroup(A,B)) = k6_autgroup(A,k2_group_1(A)) ) ) ).

fof(t27_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,B),k6_autgroup(A,k3_group_1(A,B))) = k6_autgroup(A,k2_group_1(A)) ) ) ).

fof(t28_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => k6_autgroup(A,k3_group_1(A,B)) = k2_funct_1(k6_autgroup(A,B)) ) ) ).

fof(t29_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m1_subset_1(B,u1_struct_0(A))
         => ( k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,k2_group_1(A)),k6_autgroup(A,B)) = k6_autgroup(A,B)
            & k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,B),k6_autgroup(A,k2_group_1(A))) = k6_autgroup(A,B) ) ) ) ).

fof(t30_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ! [B] :
          ( m2_fraenkel(B,u1_struct_0(A),u1_struct_0(A),k4_autgroup(A))
         => ( k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),k6_autgroup(A,k2_group_1(A)),B) = B
            & k7_funct_2(u1_struct_0(A),u1_struct_0(A),u1_struct_0(A),B,k6_autgroup(A,k2_group_1(A))) = B ) ) ) ).

fof(t31_autgroup,axiom,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => r2_group_6(k5_autgroup(A),k6_group_6(A,k10_group_5(A))) ) ).

fof(t32_autgroup,conjecture,
    ! [A] :
      ( ( ~ v3_struct_0(A)
        & v1_group_1(A)
        & v3_group_1(A)
        & v4_group_1(A)
        & l1_group_1(A) )
     => ( ( ~ v3_struct_0(A)
          & v3_group_1(A)
          & v4_group_1(A)
          & v7_group_1(A)
          & l1_group_1(A) )
       => ! [B] :
            ( m1_subset_1(B,u1_struct_0(k5_autgroup(A)))
           => B = k2_group_1(k5_autgroup(A)) ) ) ) ).

%------------------------------------------------------------------------------
