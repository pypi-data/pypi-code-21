
ERBB_BN = """fEGF := TRUE;
fERBB1 := EGF;
fERBB2 := EGF;
fERBB3 := EGF;
fERBB1_2 := ERBB1 & ERBB2;
fERBB1_3 := ERBB1 & ERBB3;
fERBB2_3 := ERBB2 & ERBB3;
fIGF1R := (ERa | AKT1) & !ERBB2_3;
fERa := AKT1 | MEK1;
fcMYC := AKT1 | MEK1 | ERa;
fAKT1 := ERBB1 | ERBB1_2 | ERBB1_3 | ERBB2_3 | IGF1R;
fMEK1 := ERBB1 | ERBB1_2 | ERBB1_3 | ERBB2_3 | IGF1R;
fCDK2 := CycE1 & !p21 & !p27;
fCDK4 := CycD1 & !p21 & !p27;
fCDK6 := CycD1;
fCycD1 := AKT1 | MEK1 | ERa | cMYC;
fCycE1 := cMYC;
fp21 := ERa & !AKT1 & !cMYC & !CDK4;
fp27 := ERa & !CDK4 & !CDK2 & !AKT1 & !cMYC;
fpRB := (CDK4 & CDK6);"""

