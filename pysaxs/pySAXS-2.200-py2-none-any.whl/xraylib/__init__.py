'''from _xraylib import \
     ( AVOGNUM ,  AtomicLevelWidth ,  AtomicNumberToSymbol , \
       AtomicWeight ,  AugerRate ,  CS_Compt ,  CS_Compt_CP ,  CS_FluorLine ,\
         CS_FluorLine_Kissel ,  CS_FluorLine_Kissel_Cascade ,  CS_FluorLine_Kissel_Nonradiative_Cascade\
          ,  CS_FluorLine_Kissel_Radiative_Cascade ,  CS_FluorLine_Kissel_no_Cascade ,\
            CS_KN ,  CS_Photo ,  CS_Photo_CP ,  CS_Photo_Partial ,  CS_Photo_Total , \
             CS_Photo_Total_CP ,  CS_Rayl ,  CS_Rayl_CP ,  CS_Total ,  CS_Total_CP , \
              CS_Total_Kissel ,  CS_Total_Kissel_CP ,  CSb_Compt ,  CSb_Compt_CP , \
               CSb_FluorLine ,  CSb_FluorLine_Kissel ,  CSb_FluorLine_Kissel_Cascade ,\
                CSb_FluorLine_Kissel_Nonradiative_Cascade ,  CSb_FluorLine_Kissel_Radiative_Cascade ,\
                  CSb_FluorLine_Kissel_no_Cascade ,  CSb_Photo ,  CSb_Photo_CP ,  CSb_Photo_Partial , \
                   CSb_Photo_Total ,  CSb_Photo_Total_CP ,  CSb_Rayl ,  CSb_Rayl_CP ,  CSb_Total ,\
                     CSb_Total_CP ,  CSb_Total_Kissel ,  CSb_Total_Kissel_CP ,  CompoundParser , \
                      ComptonEnergy ,  ComptonProfile ,  ComptonProfile_Partial ,  CosKronTransProb ,\
                        DCSP_Compt ,  DCSP_Compt_CP ,  DCSP_KN ,  DCSP_Rayl ,  DCSP_Rayl_CP ,\
                          DCSP_Thoms ,  DCSPb_Compt ,  DCSPb_Compt_CP ,  DCSPb_Rayl ,  DCSPb_Rayl_CP , \
                           DCS_Compt ,  DCS_Compt_CP ,  DCS_KN ,  DCS_Rayl ,  DCS_Rayl_CP ,  DCS_Thoms , \
                            DCSb_Compt ,  DCSb_Compt_CP ,  DCSb_Rayl ,  DCSb_Rayl_CP ,  EdgeEnergy ,  \
                            ElectronConfig ,  F12_TRANS ,  F13_TRANS ,  F1_TRANS ,  F23_TRANS , \
                             FF_Rayl ,  FL12_TRANS ,  FL13_TRANS ,  FL23_TRANS ,  FLP13_TRANS ,  FM12_TRANS , \
       FM13_TRANS ,  FM14_TRANS ,  FM15_TRANS ,  FM23_TRANS ,  FM24_TRANS ,  FM25_TRANS ,  FM34_TRANS ,  FM35_TRANS \
       ,  FM45_TRANS ,  FP13_TRANS ,  Fi ,  Fii ,  FluorYield ,  GetErrorMessages ,  GetExitStatus ,  JumpFactor ,  KA1_LINE , \
       KA2_LINE ,  KA_LINE ,  KB1_LINE ,  KB2_LINE ,  KB3_LINE ,  KB4_LINE ,  KB5_LINE ,  KB_LINE ,  KEV2ANGST ,  KL1_LINE ,\
       KL2_LINE ,  KL3_LINE ,  KM1_LINE ,  KM2_LINE ,  KM3_LINE ,  KM4_LINE ,  KM5_LINE ,  KN1_LINE ,  KN2_LINE , \
       KN3_LINE ,  KN4_LINE ,  KN5_LINE ,  KN6_LINE ,  KN7_LINE ,  KO1_LINE ,  KO2_LINE ,  KO3_LINE ,  KO4_LINE ,\
       KO5_LINE ,  KO6_LINE ,  KO7_LINE ,  KO_LINE ,  KP1_LINE ,  KP2_LINE ,  KP3_LINE ,  KP4_LINE ,  KP5_LINE ,  \
       KP_LINE ,  K_L1L1_AUGER ,  K_L1L2_AUGER ,  K_L1L3_AUGER ,  K_L1M1_AUGER ,  K_L1M2_AUGER ,  K_L1M3_AUGER , \
       K_L1M4_AUGER ,  K_L1M5_AUGER ,  K_L2L1_AUGER ,  K_L2L2_AUGER ,  K_L2L3_AUGER ,  K_L2M1_AUGER ,  \
       K_L2M2_AUGER ,  K_L2M3_AUGER ,  K_L2M4_AUGER ,  K_L2M5_AUGER ,  K_L3L1_AUGER ,  K_L3L2_AUGER , \
       K_L3L3_AUGER ,  K_L3M1_AUGER ,  K_L3M2_AUGER ,  K_L3M3_AUGER ,  K_L3M4_AUGER ,  K_L3M5_AUGER , \
       K_M1L1_AUGER ,  K_M1L2_AUGER ,  K_M1L3_AUGER ,  K_M1M1_AUGER ,  K_M1M2_AUGER ,  K_M1M3_AUGER , \
       K_M1M4_AUGER ,  K_M1M5_AUGER ,  K_M2L1_AUGER ,  K_M2L2_AUGER ,  K_M2L3_AUGER ,  K_M2M1_AUGER , \
       K_M2M2_AUGER ,  K_M2M3_AUGER ,  K_M2M4_AUGER ,  K_M2M5_AUGER ,  K_M3L1_AUGER ,  K_M3L2_AUGER , \
       K_M3L3_AUGER ,  K_M3M1_AUGER ,  K_M3M2_AUGER ,  K_M3M3_AUGER ,  K_M3M4_AUGER ,  K_M3M5_AUGER , \
       K_M4L1_AUGER ,  K_M4L2_AUGER ,  K_M4L3_AUGER ,  K_M4M1_AUGER ,  K_M4M2_AUGER ,  K_M4M3_AUGER ,  \
       K_M4M4_AUGER ,  K_M4M5_AUGER ,  K_M5L1_AUGER ,  K_M5L2_AUGER ,  K_M5L3_AUGER ,  K_M5M1_AUGER ,  \
       K_M5M2_AUGER ,  K_M5M3_AUGER ,  K_M5M4_AUGER ,  K_M5M5_AUGER ,  K_SHELL ,  L1L2_LINE ,  \
       L1L3_LINE ,  L1M1_LINE ,  L1M2_LINE ,  L1M3_LINE ,  L1M4_LINE ,  L1M5_LINE ,  L1N1_LINE ,  \
       L1N2_LINE ,  L1N3_LINE ,  L1N4_LINE ,  L1N5_LINE ,  L1N67_LINE ,  L1N6_LINE ,  L1N7_LINE , \
       L1O1_LINE ,  L1O2_LINE ,  L1O3_LINE ,  L1O45_LINE ,  L1O4_LINE ,  L1O5_LINE ,  L1O6_LINE ,  \
       L1O7_LINE ,  L1P1_LINE ,  L1P23_LINE ,  L1P2_LINE ,  L1P3_LINE ,  L1P4_LINE ,  L1P5_LINE , \
       L1_L2L2_AUGER ,  L1_L2L3_AUGER ,  L1_L2M1_AUGER ,  L1_L2M2_AUGER ,  L1_L2M3_AUGER ,  \
       L1_L2M4_AUGER ,  L1_L2M5_AUGER ,  L1_L3L2_AUGER ,  L1_L3L3_AUGER ,  L1_L3M1_AUGER ,  L1_L3M2_AUGER ,\
       L1_L3M3_AUGER ,  L1_L3M4_AUGER ,  L1_L3M5_AUGER ,  L1_M1L2_AUGER ,  L1_M1L3_AUGER ,  L1_M1M1_AUGER ,  \
       L1_M1M2_AUGER ,  L1_M1M3_AUGER ,  L1_M1M4_AUGER ,  L1_M1M5_AUGER ,  L1_M2L2_AUGER ,  L1_M2L3_AUGER ,  L1_M2M1_AUGER ,  \
       L1_M2M2_AUGER ,  L1_M2M3_AUGER ,  L1_M2M4_AUGER ,  L1_M2M5_AUGER ,  L1_M3L2_AUGER ,  L1_M3L3_AUGER ,  L1_M3M1_AUGER , \
       L1_M3M2_AUGER ,  L1_M3M3_AUGER ,  L1_M3M4_AUGER ,  L1_M3M5_AUGER ,  L1_M4L2_AUGER ,  L1_M4L3_AUGER ,  L1_M4M1_AUGER , \
       L1_M4M2_AUGER ,  L1_M4M3_AUGER ,  L1_M4M4_AUGER ,  L1_M4M5_AUGER ,  L1_M5L2_AUGER ,  L1_M5L3_AUGER ,  L1_M5M1_AUGER ,  \
       L1_M5M2_AUGER ,  L1_M5M3_AUGER ,  L1_M5M4_AUGER ,  L1_M5M5_AUGER ,  L1_SHELL ,  L2L3_LINE ,  L2M1_LINE ,  L2M2_LINE , \
       L2M3_LINE ,  L2M4_LINE ,  L2M5_LINE ,  L2N1_LINE ,  L2N2_LINE ,  L2N3_LINE ,  L2N4_LINE ,  L2N5_LINE ,  L2N6_LINE ,  \
       L2N7_LINE ,  L2O1_LINE ,  L2O2_LINE ,  L2O3_LINE ,  L2O4_LINE ,  L2O5_LINE ,  L2O6_LINE ,  L2O7_LINE ,  L2P1_LINE ,  \
       L2P23_LINE ,  L2P2_LINE ,  L2P3_LINE ,  L2P4_LINE ,  L2P5_LINE ,  L2Q1_LINE ,  L2_L3L3_AUGER ,  L2_L3M1_AUGER , \
       L2_L3M2_AUGER ,  L2_L3M3_AUGER ,  L2_L3M4_AUGER ,  L2_L3M5_AUGER ,  L2_M1L3_AUGER ,  L2_M1M1_AUGER ,  L2_M1M2_AUGER , \
       L2_M1M3_AUGER ,  L2_M1M4_AUGER ,  L2_M1M5_AUGER ,  L2_M2L3_AUGER ,  L2_M2M1_AUGER ,  L2_M2M2_AUGER ,  L2_M2M3_AUGER , \
       L2_M2M4_AUGER ,  L2_M2M5_AUGER ,  L2_M3L3_AUGER ,  L2_M3M1_AUGER ,  L2_M3M2_AUGER ,  L2_M3M3_AUGER ,  L2_M3M4_AUGER ,  \
       L2_M3M5_AUGER ,  L2_M4L3_AUGER ,  L2_M4M1_AUGER ,  L2_M4M2_AUGER ,  L2_M4M3_AUGER ,  L2_M4M4_AUGER ,  L2_M4M5_AUGER , \
       L2_M5L3_AUGER ,  L2_M5M1_AUGER ,  L2_M5M2_AUGER ,  L2_M5M3_AUGER ,  L2_M5M4_AUGER ,  L2_M5M5_AUGER ,  L2_SHELL ,  L3M1_LINE ,\
       L3M2_LINE ,  L3M3_LINE ,  L3M4_LINE ,  L3M5_LINE ,  L3N1_LINE ,  L3N2_LINE ,  L3N3_LINE ,  L3N4_LINE , \
       L3N5_LINE ,  L3N6_LINE ,  L3N7_LINE ,  L3O1_LINE ,  L3O2_LINE ,  L3O3_LINE ,  L3O45_LINE ,  L3O4_LINE ,\
       L3O5_LINE ,  L3O6_LINE ,  L3O7_LINE ,  L3P1_LINE ,  L3P23_LINE ,  L3P2_LINE ,  L3P3_LINE ,  L3P45_LINE ,  \
       L3P4_LINE ,  L3P5_LINE ,  L3Q1_LINE ,  L3_M1M1_AUGER ,  L3_M1M2_AUGER ,  L3_M1M3_AUGER ,  L3_M1M4_AUGER ,\
       L3_M1M5_AUGER ,  L3_M2M1_AUGER ,  L3_M2M2_AUGER ,  L3_M2M3_AUGER ,  L3_M2M4_AUGER ,  L3_M2M5_AUGER , \
       L3_M3M1_AUGER ,  L3_M3M2_AUGER ,  L3_M3M3_AUGER ,  L3_M3M4_AUGER ,  L3_M3M5_AUGER ,  L3_M4M1_AUGER , \
       L3_M4M2_AUGER ,  L3_M4M3_AUGER ,  L3_M4M4_AUGER ,  L3_M4M5_AUGER ,  L3_M5M1_AUGER ,  L3_M5M2_AUGER ,  \
       L3_M5M3_AUGER ,  L3_M5M4_AUGER ,  L3_M5M5_AUGER ,  L3_SHELL ,  LA1_LINE ,  LA2_LINE ,  LA_LINE , \
       LB10_LINE ,  LB15_LINE ,  LB17_LINE ,  LB1_LINE ,  LB2_LINE ,  LB3_LINE ,  LB4_LINE ,  LB5_LINE ,  \
       LB6_LINE ,  LB7_LINE ,  LB9_LINE ,  LB_LINE ,  LE_LINE ,  LG1_LINE ,  LG2_LINE ,  LG3_LINE ,  LG4_LINE , \
       LG5_LINE ,  LG6_LINE ,  LG8_LINE ,  LL_LINE ,  LS_LINE ,  LT_LINE ,  LU_LINE ,  LV_LINE ,  LineEnergy , \
       M1M2_LINE ,  M1M3_LINE ,  M1M4_LINE ,  M1M5_LINE ,  M1N1_LINE ,  M1N2_LINE ,  M1N3_LINE ,  M1N4_LINE , \
       M1N5_LINE ,  M1N6_LINE ,  M1N7_LINE ,  M1O1_LINE ,  M1O2_LINE ,  M1O3_LINE ,  M1O4_LINE ,  M1O5_LINE ,  \
       M1O6_LINE ,  M1O7_LINE ,  M1P1_LINE ,  M1P2_LINE ,  M1P3_LINE ,  M1P4_LINE ,  M1P5_LINE ,  M1_M2M2_AUGER , \
       M1_M2M3_AUGER ,  M1_M2M4_AUGER ,  M1_M2M5_AUGER ,  M1_M3M2_AUGER ,  M1_M3M3_AUGER ,  M1_M3M4_AUGER , \
       M1_M3M5_AUGER ,  M1_M4M2_AUGER ,  M1_M4M3_AUGER ,  M1_M4M4_AUGER ,  M1_M4M5_AUGER ,  M1_M5M2_AUGER ,  \
       M1_M5M3_AUGER ,  M1_M5M4_AUGER ,  M1_M5M5_AUGER ,  M1_SHELL ,  M2M3_LINE ,  M2M4_LINE ,  M2M5_LINE ,  \
       M2N1_LINE ,  M2N2_LINE ,  M2N3_LINE ,  M2N4_LINE ,  M2N5_LINE ,  M2N6_LINE ,  M2N7_LINE ,  M2O1_LINE ,  \
       M2O2_LINE ,  M2O3_LINE ,  M2O4_LINE ,  M2O5_LINE ,  M2O6_LINE ,  M2O7_LINE ,  M2P1_LINE ,  M2P2_LINE , \
       M2P3_LINE ,  M2P4_LINE ,  M2P5_LINE ,  M2_M3M3_AUGER ,  M2_M3M4_AUGER ,  M2_M3M5_AUGER ,  M2_M4M3_AUGER , \
       M2_M4M4_AUGER ,  M2_M4M5_AUGER ,  M2_M5M3_AUGER ,  M2_M5M4_AUGER ,  M2_M5M5_AUGER ,  M2_SHELL ,  M3M4_LINE , \
       M3M5_LINE ,  M3N1_LINE ,  M3N2_LINE ,  M3N3_LINE ,  M3N4_LINE ,  M3N5_LINE ,  M3N6_LINE ,  M3N7_LINE , \
       M3O1_LINE ,  M3O2_LINE ,  M3O3_LINE ,  M3O4_LINE ,  M3O5_LINE ,  M3O6_LINE ,  M3O7_LINE ,  M3P1_LINE ,  \
       M3P2_LINE ,  M3P3_LINE ,  M3P4_LINE ,  M3P5_LINE ,  M3Q1_LINE ,  M3_M4M4_AUGER ,  M3_M4M5_AUGER , \
       M3_M5M4_AUGER ,  M3_M5M5_AUGER ,  M3_SHELL ,  M4M5_LINE ,  M4N1_LINE ,  M4N2_LINE ,  M4N3_LINE ,  \
       M4N4_LINE ,  M4N5_LINE ,  M4N6_LINE ,  M4N7_LINE ,  M4O1_LINE ,  M4O2_LINE ,  M4O3_LINE ,  M4O4_LINE , \
       M4O5_LINE ,  M4O6_LINE ,  M4O7_LINE ,  M4P1_LINE ,  M4P2_LINE ,  M4P3_LINE ,  M4P4_LINE ,  M4P5_LINE , \
       M4_M5M5_AUGER ,  M4_SHELL ,  M5N1_LINE ,  M5N2_LINE ,  M5N3_LINE ,  M5N4_LINE ,  M5N5_LINE ,  M5N6_LINE , \
       M5N7_LINE ,  M5O1_LINE ,  M5O2_LINE ,  M5O3_LINE ,  M5O4_LINE ,  M5O5_LINE ,  M5O6_LINE ,  M5O7_LINE , \
       M5P1_LINE ,  M5P2_LINE ,  M5P3_LINE ,  M5P4_LINE ,  M5P5_LINE ,  M5_SHELL ,  MA1_LINE ,  MA2_LINE , \
       MB_LINE ,  MEC2 ,  MG_LINE ,  MomentTransf ,  N1N2_LINE ,  N1N3_LINE ,  N1N4_LINE ,  N1N5_LINE , \
       N1N6_LINE ,  N1N7_LINE ,  N1O1_LINE ,  N1O2_LINE ,  N1O3_LINE ,  N1O4_LINE ,  N1O5_LINE ,  N1O6_LINE , \
       N1O7_LINE ,  N1P1_LINE ,  N1P2_LINE ,  N1P3_LINE ,  N1P4_LINE ,  N1P5_LINE ,  N1_SHELL ,  N2N3_LINE , \
       N2N4_LINE ,  N2N5_LINE ,  N2N6_LINE ,  N2N7_LINE ,  N2O1_LINE ,  N2O2_LINE ,  N2O3_LINE ,  N2O4_LINE , \
       N2O5_LINE ,  N2O6_LINE ,  N2O7_LINE ,  N2P1_LINE ,  N2P2_LINE ,  N2P3_LINE ,  N2P4_LINE ,  N2P5_LINE , \
       N2_SHELL ,  N3N4_LINE ,  N3N5_LINE ,  N3N6_LINE ,  N3N7_LINE ,  N3O1_LINE ,  N3O2_LINE ,  N3O3_LINE , \
       N3O4_LINE ,  N3O5_LINE ,  N3O6_LINE ,  N3O7_LINE ,  N3P1_LINE ,  N3P2_LINE ,  N3P3_LINE ,  N3P4_LINE , \
       N3P5_LINE ,  N3_SHELL ,  N4N5_LINE ,  N4N6_LINE ,  N4N7_LINE ,  N4O1_LINE ,  N4O2_LINE ,  N4O3_LINE , \
       N4O4_LINE ,  N4O5_LINE ,  N4O6_LINE ,  N4O7_LINE ,  N4P1_LINE ,  N4P2_LINE ,  N4P3_LINE ,  N4P4_LINE ,\
       N4P5_LINE ,  N4_SHELL ,  N5N6_LINE ,  N5N7_LINE ,  N5O1_LINE ,  N5O2_LINE ,  N5O3_LINE ,  N5O4_LINE , \
       N5O5_LINE ,  N5O6_LINE ,  N5O7_LINE ,  N5P1_LINE ,  N5P2_LINE ,  N5P3_LINE ,  N5P4_LINE ,  N5P5_LINE ,\
       N5_SHELL ,  N6N7_LINE ,  N6O1_LINE ,  N6O2_LINE ,  N6O3_LINE ,  N6O4_LINE ,  N6O5_LINE ,  N6O6_LINE , \
       N6O7_LINE ,  N6P1_LINE ,  N6P2_LINE ,  N6P3_LINE ,  N6P4_LINE ,  N6P5_LINE ,  N6_SHELL ,  N7O1_LINE , \
       N7O2_LINE ,  N7O3_LINE ,  N7O4_LINE ,  N7O5_LINE ,  N7O6_LINE ,  N7O7_LINE ,  N7P1_LINE ,  N7P2_LINE ,\
       N7P3_LINE ,  N7P4_LINE ,  N7P5_LINE ,  N7_SHELL ,  O1O2_LINE ,  O1O3_LINE ,  O1O4_LINE ,  O1O5_LINE , \
       O1O6_LINE ,  O1O7_LINE ,  O1P1_LINE ,  O1P2_LINE ,  O1P3_LINE ,  O1P4_LINE ,  O1P5_LINE ,  O1_SHELL , \
       O2O3_LINE ,  O2O4_LINE ,  O2O5_LINE ,  O2O6_LINE ,  O2O7_LINE ,  O2P1_LINE ,  O2P2_LINE ,  O2P3_LINE ,\
       O2P4_LINE ,  O2P5_LINE ,  O2_SHELL ,  O3O4_LINE ,  O3O5_LINE ,  O3O6_LINE ,  O3O7_LINE ,  O3P1_LINE , \
       O3P2_LINE ,  O3P3_LINE ,  O3P4_LINE ,  O3P5_LINE ,  O3_SHELL ,  O4O5_LINE ,  O4O6_LINE ,  O4O7_LINE ,   \
       O4P1_LINE ,  O4P2_LINE ,  O4P3_LINE ,  O4P4_LINE ,  O4P5_LINE ,  O4_SHELL ,  O5O6_LINE ,  O5O7_LINE ,   \
       O5P1_LINE ,  O5P2_LINE ,  O5P3_LINE ,  O5P4_LINE ,  O5P5_LINE ,  O5_SHELL ,  O6O7_LINE ,  O6P4_LINE ,   \
       O6P5_LINE ,  O6_SHELL ,  O7P4_LINE ,  O7P5_LINE ,  O7_SHELL ,  P1P2_LINE ,  P1P3_LINE ,  P1P4_LINE ,  \
        P1P5_LINE ,  P1_SHELL ,  P2P3_LINE ,  P2P4_LINE ,  P2P5_LINE ,  P2_SHELL ,  P3P4_LINE ,  P3P5_LINE , \
         P3_SHELL ,  P4_SHELL ,  P5_SHELL ,  PI ,  Q1_SHELL ,  Q2_SHELL ,  Q3_SHELL ,  RE2 ,  RadRate ,   \
       Refractive_Index_Im ,  Refractive_Index_Re ,  SF_Compt ,  SWIG_PyInstanceMethod_New ,  SetErrorMessages , \
         SetExitStatus ,  SetHardExit ,  SymbolToAtomicNumber ,  XRAYLIB_MAJOR ,  XRAYLIB_MINOR ,  \
        XRayInit ,  __doc__ ,  __file__ ,  __name__ ,  __package__ ,  _free_compound_data ,  add_compound_data , \
         compoundData_Elements_get ,  compoundData_Elements_set ,  compoundData_massFractions_get ,  \
        compoundData_massFractions_set ,  compoundData_nAtomsAll_get ,  compoundData_nAtomsAll_set ,  compoundData_nElements_get , \
       compoundData_nElements_set ,  compoundData_swigregister ,  delete_compoundData ,  new_compoundData ,  xrlFree )
'''
from _xraylib import *
