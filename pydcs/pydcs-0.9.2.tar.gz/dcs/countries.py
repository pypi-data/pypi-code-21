# This file is generated from pydcs_export.lua

from .country import Country
from . import vehicles
from . import planes
from . import helicopters
from . import ships


class Russia(Country):
    id = 0
    name = "Russia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Paratrooper_RPG_16 = vehicles.Infantry.Paratrooper_RPG_16
            Paratrooper_AKS = vehicles.Infantry.Paratrooper_AKS
            Infantry_Soldier_Rus = vehicles.Infantry.Infantry_Soldier_Rus

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_Ural_4320_31_Armored = vehicles.Unarmed.Transport_Ural_4320_31_Armored
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320
            APC_Tigr_233036 = vehicles.Unarmed.APC_Tigr_233036

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            MBT_T_80U = vehicles.Armor.MBT_T_80U
            IFV_BMP_3 = vehicles.Armor.IFV_BMP_3
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55
            ARV_MTLB_U_BOMAN = vehicles.Armor.ARV_MTLB_U_BOMAN
            MBT_T_90 = vehicles.Armor.MBT_T_90

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S19_Msta = vehicles.Artillery.SPH_2S19_Msta
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            MLRS_9K57_Uragan_BM_27 = vehicles.Artillery.MLRS_9K57_Uragan_BM_27
            MLRS_9A52_Smerch = vehicles.Artillery.MLRS_9A52_Smerch
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            EWR_1L13 = vehicles.AirDefence.EWR_1L13
            EWR_55G6 = vehicles.AirDefence.EWR_55G6
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_6_Kub_STR_9S91 = vehicles.AirDefence.SAM_SA_6_Kub_STR_9S91
            SAM_SA_6_Kub_LN_2P25 = vehicles.AirDefence.SAM_SA_6_Kub_LN_2P25
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_18_Igla_S_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_S_MANPADS
            SAM_SA_18_Igla_S_comm = vehicles.AirDefence.SAM_SA_18_Igla_S_comm
            SAM_SA_3_S_125_LN_5P73 = vehicles.AirDefence.SAM_SA_3_S_125_LN_5P73
            SAM_SA_3_S_125_TR_SNR = vehicles.AirDefence.SAM_SA_3_S_125_TR_SNR
            SAM_SA_3_S_125_SR_P_19 = vehicles.AirDefence.SAM_SA_3_S_125_SR_P_19

    class Plane:
        A_10C = planes.A_10C
        Su_33 = planes.Su_33
        Su_25 = planes.Su_25
        MiG_29S = planes.MiG_29S
        MiG_29A = planes.MiG_29A
        Su_27 = planes.Su_27
        Su_25TM = planes.Su_25TM
        Su_25T = planes.Su_25T
        MiG_31 = planes.MiG_31
        MiG_27K = planes.MiG_27K
        Su_30 = planes.Su_30
        Tu_160 = planes.Tu_160
        Su_34 = planes.Su_34
        Tu_95MS = planes.Tu_95MS
        Tu_142 = planes.Tu_142
        MiG_25PD = planes.MiG_25PD
        Tu_22M3 = planes.Tu_22M3
        A_50 = planes.A_50
        Yak_40 = planes.Yak_40
        An_26B = planes.An_26B
        An_30M = planes.An_30M
        Su_17M4 = planes.Su_17M4
        MiG_23MLD = planes.MiG_23MLD
        MiG_25RBT = planes.MiG_25RBT
        Su_24M = planes.Su_24M
        Su_24MR = planes.Su_24MR
        IL_78M = planes.IL_78M
        IL_76MD = planes.IL_76MD
        L_39ZA = planes.L_39ZA
        P_51D = planes.P_51D
        FW_190D9 = planes.Fw_190_D_9
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.Su_33,
        Plane.Su_25,
        Plane.MiG_29S,
        Plane.MiG_29A,
        Plane.Su_27,
        Plane.Su_25TM,
        Plane.Su_25T,
        Plane.MiG_31,
        Plane.MiG_27K,
        Plane.Su_30,
        Plane.Tu_160,
        Plane.Su_34,
        Plane.Tu_95MS,
        Plane.Tu_142,
        Plane.MiG_25PD,
        Plane.Tu_22M3,
        Plane.A_50,
        Plane.Yak_40,
        Plane.An_26B,
        Plane.An_30M,
        Plane.Su_17M4,
        Plane.MiG_23MLD,
        Plane.MiG_25RBT,
        Plane.Su_24M,
        Plane.Su_24MR,
        Plane.IL_78M,
        Plane.IL_76MD,
        Plane.L_39ZA,
        Plane.P_51D,
        Plane.FW_190D9,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        Mi_26 = helicopters.Mi_26
        Ka_27 = helicopters.Ka_27
        Mi_28N = helicopters.Mi_28N
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.Mi_26,
        Helicopter.Ka_27,
        Helicopter.Mi_28N,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        CV_1143_5_Admiral_Kuznetsov = ships.CV_1143_5_Admiral_Kuznetsov
        CG_1164_Moskva = ships.CG_1164_Moskva
        CGN_1144_2_Pyotr_Velikiy = ships.CGN_1144_2_Pyotr_Velikiy
        Tanker_Elnya_160 = ships.Tanker_Elnya_160
        FFL_1124_4_Grisha = ships.FFL_1124_4_Grisha
        FF_1135M_Rezky = ships.FF_1135M_Rezky
        FSG_1241_1MP_Molniya = ships.FSG_1241_1MP_Molniya
        SSK_877 = ships.SSK_877
        SSK_641B = ships.SSK_641B
        Civil_boat_Zvezdny = ships.Civil_boat_Zvezdny
        FFG_11540_Neustrashimy = ships.FFG_11540_Neustrashimy
        Bulk_cargo_ship_Yakushev = ships.Bulk_cargo_ship_Yakushev
        Dry_cargo_ship_Ivanov = ships.Dry_cargo_ship_Ivanov

    class CallsignHelipad:
        Otkrytka = "Otkrytka"
        Vetka = "Vetka"
        Yunga = "Yunga"
        Shpora = "Shpora"
        Kalitka = "Kalitka"
        Torba = "Torba"
        Kaemka = "Kaemka"
        Podkova = "Podkova"
        Skala = "Skala"
        Kapel = "Kapel"

    callsign = {
        "Helipad": [
            CallsignHelipad.Otkrytka,
            CallsignHelipad.Vetka,
            CallsignHelipad.Yunga,
            CallsignHelipad.Shpora,
            CallsignHelipad.Kalitka,
            CallsignHelipad.Torba,
            CallsignHelipad.Kaemka,
            CallsignHelipad.Podkova,
            CallsignHelipad.Skala,
            CallsignHelipad.Kapel
        ],
    }

    def __init__(self):
        super(Russia, self).__init__(Russia.id, Russia.name)


class Ukraine(Country):
    id = 1
    name = "Ukraine"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Paratrooper_RPG_16 = vehicles.Infantry.Paratrooper_RPG_16
            Paratrooper_AKS = vehicles.Infantry.Paratrooper_AKS

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320
            Transport_KrAZ_6322 = vehicles.Unarmed.Transport_KrAZ_6322

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            IFV_BMP_3 = vehicles.Armor.IFV_BMP_3
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            MBT_T_80U = vehicles.Armor.MBT_T_80U
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S19_Msta = vehicles.Artillery.SPH_2S19_Msta
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            MLRS_9A52_Smerch = vehicles.Artillery.MLRS_9A52_Smerch
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            EWR_1L13 = vehicles.AirDefence.EWR_1L13
            EWR_55G6 = vehicles.AirDefence.EWR_55G6
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_6_Kub_STR_9S91 = vehicles.AirDefence.SAM_SA_6_Kub_STR_9S91
            SAM_SA_6_Kub_LN_2P25 = vehicles.AirDefence.SAM_SA_6_Kub_LN_2P25
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_18_Igla_S_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_S_MANPADS
            SAM_SA_18_Igla_S_comm = vehicles.AirDefence.SAM_SA_18_Igla_S_comm

    class Plane:
        A_10C = planes.A_10C
        Su_27 = planes.Su_27
        MiG_29A = planes.MiG_29A
        MiG_29S = planes.MiG_29S
        Su_17M4 = planes.Su_17M4
        Tu_95MS = planes.Tu_95MS
        Su_24M = planes.Su_24M
        Su_24MR = planes.Su_24MR
        Su_25 = planes.Su_25
        MiG_25PD = planes.MiG_25PD
        An_26B = planes.An_26B
        An_30M = planes.An_30M
        MiG_23MLD = planes.MiG_23MLD
        IL_78M = planes.IL_78M
        IL_76MD = planes.IL_76MD
        MiG_27K = planes.MiG_27K
        Tu_22M3 = planes.Tu_22M3
        MiG_25RBT = planes.MiG_25RBT
        Yak_40 = planes.Yak_40
        L_39ZA = planes.L_39ZA
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.Su_27,
        Plane.MiG_29A,
        Plane.MiG_29S,
        Plane.Su_17M4,
        Plane.Tu_95MS,
        Plane.Su_24M,
        Plane.Su_24MR,
        Plane.Su_25,
        Plane.MiG_25PD,
        Plane.An_26B,
        Plane.An_30M,
        Plane.MiG_23MLD,
        Plane.IL_78M,
        Plane.IL_76MD,
        Plane.MiG_27K,
        Plane.Tu_22M3,
        Plane.MiG_25RBT,
        Plane.Yak_40,
        Plane.L_39ZA,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        Mi_26 = helicopters.Mi_26
        Ka_27 = helicopters.Ka_27
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.Mi_26,
        Helicopter.Ka_27,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        Tanker_Elnya_160 = ships.Tanker_Elnya_160
        FFL_1124_4_Grisha = ships.FFL_1124_4_Grisha
        FSG_1241_1MP_Molniya = ships.FSG_1241_1MP_Molniya
        SSK_877 = ships.SSK_877
        Civil_boat_Zvezdny = ships.Civil_boat_Zvezdny
        Bulk_cargo_ship_Yakushev = ships.Bulk_cargo_ship_Yakushev
        Dry_cargo_ship_Ivanov = ships.Dry_cargo_ship_Ivanov
        FF_1135M_Rezky = ships.FF_1135M_Rezky

    def __init__(self):
        super(Ukraine, self).__init__(Ukraine.id, Ukraine.name)


class USA(Country):
    id = 2
    name = "USA"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_M4 = vehicles.Infantry.Infantry_M4
            Soldier_M249 = vehicles.Infantry.Soldier_M249
            Infantry_M1_Garand = vehicles.Infantry.Infantry_M1_Garand

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            CP_Predator_GCS = vehicles.Unarmed.CP_Predator_GCS
            CP_Predator_TrojanSpirit = vehicles.Unarmed.CP_Predator_TrojanSpirit
            Tanker_M978_HEMTT = vehicles.Unarmed.Tanker_M978_HEMTT
            HEMTT_TFFT = vehicles.Unarmed.HEMTT_TFFT
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            IFV_M2A2_Bradley = vehicles.Armor.IFV_M2A2_Bradley
            IFV_LAV_25 = vehicles.Armor.IFV_LAV_25
            APC_AAV_7 = vehicles.Armor.APC_AAV_7
            APC_M113 = vehicles.Armor.APC_M113
            MBT_M1A2_Abrams = vehicles.Armor.MBT_M1A2_Abrams
            APC_M1126_Stryker_ICV = vehicles.Armor.APC_M1126_Stryker_ICV
            SPG_M1128_Stryker_MGS = vehicles.Armor.SPG_M1128_Stryker_MGS
            ATGM_M1134_Stryker = vehicles.Armor.ATGM_M1134_Stryker
            APC_M1043_HMMWV_Armament = vehicles.Armor.APC_M1043_HMMWV_Armament
            ATGM_M1045_HMMWV_TOW = vehicles.Armor.ATGM_M1045_HMMWV_TOW
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_Avenger_M1097 = vehicles.AirDefence.SAM_Avenger_M1097
            SAM_Patriot_STR_AN_MPQ_53 = vehicles.AirDefence.SAM_Patriot_STR_AN_MPQ_53
            SAM_Patriot_LN_M901 = vehicles.AirDefence.SAM_Patriot_LN_M901
            SAM_Patriot_AMG_AN_MRC_137 = vehicles.AirDefence.SAM_Patriot_AMG_AN_MRC_137
            SAM_Patriot_EPP_III = vehicles.AirDefence.SAM_Patriot_EPP_III
            SAM_Patriot_ECS_AN_MSQ_104 = vehicles.AirDefence.SAM_Patriot_ECS_AN_MSQ_104
            SAM_Patriot_ICC = vehicles.AirDefence.SAM_Patriot_ICC
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            AAA_Vulcan_M163 = vehicles.AirDefence.AAA_Vulcan_M163
            SAM_Chaparral_M48 = vehicles.AirDefence.SAM_Chaparral_M48
            SAM_Linebacker_M6 = vehicles.AirDefence.SAM_Linebacker_M6
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        A_10A = planes.A_10A
        F_117A = planes.F_117A
        C_17A = planes.C_17A
        F_15C = planes.F_15C
        F_15E = planes.F_15E
        F_16C_bl_52d = planes.F_16C_bl_52d
        B_1B = planes.B_1B
        B_52H = planes.B_52H
        E_3A = planes.E_3A
        KC_135 = planes.KC_135
        C_130 = planes.C_130
        F_14A = planes.F_14A
        S_3B = planes.S_3B
        S_3B_Tanker = planes.S_3B_Tanker
        F_A_18C = planes.F_A_18C
        E_2C = planes.E_2D
        F_16A = planes.F_16A
        RQ_1A_Predator = planes.MQ_1A_Predator
        P_51D = planes.P_51D
        L_39ZA = planes.L_39ZA
        FW_190D9 = planes.Fw_190_D_9
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MQ_9_Reaper = planes.MQ_9_Reaper
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        B_17G = planes.B_17G
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.A_10A,
        Plane.F_117A,
        Plane.C_17A,
        Plane.F_15C,
        Plane.F_15E,
        Plane.F_16C_bl_52d,
        Plane.B_1B,
        Plane.B_52H,
        Plane.E_3A,
        Plane.KC_135,
        Plane.C_130,
        Plane.F_14A,
        Plane.S_3B,
        Plane.S_3B_Tanker,
        Plane.F_A_18C,
        Plane.E_2C,
        Plane.F_16A,
        Plane.RQ_1A_Predator,
        Plane.P_51D,
        Plane.L_39ZA,
        Plane.FW_190D9,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MQ_9_Reaper,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.B_17G,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        AH_64A = helicopters.AH_64A
        AH_64D = helicopters.AH_64D
        AH_1W = helicopters.AH_1W
        UH_60A = helicopters.UH_60A
        CH_47D = helicopters.CH_47D
        SH_60B = helicopters.SH_60B
        CH_53E = helicopters.CH_53E
        OH_58D = helicopters.OH_58D
        UH_1H = helicopters.UH_1H
        Mi_8MT = helicopters.Mi_8MTV2
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.AH_64A,
        Helicopter.AH_64D,
        Helicopter.AH_1W,
        Helicopter.UH_60A,
        Helicopter.CH_47D,
        Helicopter.SH_60B,
        Helicopter.CH_53E,
        Helicopter.OH_58D,
        Helicopter.UH_1H,
        Helicopter.Mi_8MT,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        CVN_70_Carl_Vinson = ships.CVN_70_Carl_Vinson
        FFG_7CL_Oliver_Hazzard_Perry = ships.FFG_7CL_Oliver_Hazzard_Perry
        CG_60_Normandy = ships.CG_60_Normandy
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    class CallsignAWACS:
        Overlord = "Overlord"
        Magic = "Magic"
        Wizard = "Wizard"
        Focus = "Focus"
        Darkstar = "Darkstar"

    class CallsignAir:
        Enfield = "Enfield"
        Springfield = "Springfield"
        Uzi = "Uzi"
        Colt = "Colt"
        Dodge = "Dodge"
        Ford = "Ford"
        Chevy = "Chevy"
        Pontiac = "Pontiac"

    class CallsignHelipad:
        London = "London"
        Dallas = "Dallas"
        Paris = "Paris"
        Moscow = "Moscow"
        Berlin = "Berlin"
        Rome = "Rome"
        Madrid = "Madrid"
        Warsaw = "Warsaw"
        Dublin = "Dublin"
        Perth = "Perth"

    class CallsignGroundUnits:
        Axeman = "Axeman"
        Darknight = "Darknight"
        Warrior = "Warrior"
        Pointer = "Pointer"
        Eyeball = "Eyeball"
        Moonbeam = "Moonbeam"
        Whiplash = "Whiplash"
        Finger = "Finger"
        Pinpoint = "Pinpoint"
        Ferret = "Ferret"
        Shaba = "Shaba"
        Playboy = "Playboy"
        Hammer = "Hammer"
        Jaguar = "Jaguar"
        Deathstar = "Deathstar"
        Anvil = "Anvil"
        Firefly = "Firefly"
        Mantis = "Mantis"
        Badger = "Badger"

    callsign = {
        "AWACS": [
            CallsignAWACS.Overlord,
            CallsignAWACS.Magic,
            CallsignAWACS.Wizard,
            CallsignAWACS.Focus,
            CallsignAWACS.Darkstar
        ],
        "Air": [
            CallsignAir.Enfield,
            CallsignAir.Springfield,
            CallsignAir.Uzi,
            CallsignAir.Colt,
            CallsignAir.Dodge,
            CallsignAir.Ford,
            CallsignAir.Chevy,
            CallsignAir.Pontiac
        ],
        "Helipad": [
            CallsignHelipad.London,
            CallsignHelipad.Dallas,
            CallsignHelipad.Paris,
            CallsignHelipad.Moscow,
            CallsignHelipad.Berlin,
            CallsignHelipad.Rome,
            CallsignHelipad.Madrid,
            CallsignHelipad.Warsaw,
            CallsignHelipad.Dublin,
            CallsignHelipad.Perth
        ],
        "GroundUnits": [
            CallsignGroundUnits.Axeman,
            CallsignGroundUnits.Darknight,
            CallsignGroundUnits.Warrior,
            CallsignGroundUnits.Pointer,
            CallsignGroundUnits.Eyeball,
            CallsignGroundUnits.Moonbeam,
            CallsignGroundUnits.Whiplash,
            CallsignGroundUnits.Finger,
            CallsignGroundUnits.Pinpoint,
            CallsignGroundUnits.Ferret,
            CallsignGroundUnits.Shaba,
            CallsignGroundUnits.Playboy,
            CallsignGroundUnits.Hammer,
            CallsignGroundUnits.Jaguar,
            CallsignGroundUnits.Deathstar,
            CallsignGroundUnits.Anvil,
            CallsignGroundUnits.Firefly,
            CallsignGroundUnits.Mantis,
            CallsignGroundUnits.Badger
        ],
    }

    def __init__(self):
        super(USA, self).__init__(USA.id, USA.name)


class Turkey(Country):
    id = 3
    name = "Turkey"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Tanker_M978_HEMTT = vehicles.Unarmed.Tanker_M978_HEMTT
            HEMTT_TFFT = vehicles.Unarmed.HEMTT_TFFT

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            APC_Cobra = vehicles.Armor.APC_Cobra
            MBT_M60A3_Patton = vehicles.Armor.MBT_M60A3_Patton
            APC_AAV_7 = vehicles.Armor.APC_AAV_7
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            MLRS_M270 = vehicles.Artillery.MLRS_M270
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            SAM_Avenger_M1097 = vehicles.AirDefence.SAM_Avenger_M1097
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm

    class Plane:
        A_10C = planes.A_10C
        F_16C_bl_50 = planes.F_16C_bl_50
        F_4E = planes.F_4E
        C_130 = planes.C_130
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MQ_9_Reaper = planes.MQ_9_Reaper
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.F_16C_bl_50,
        Plane.F_4E,
        Plane.C_130,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MQ_9_Reaper,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        UH_60A = helicopters.UH_60A
        Mi_8MT = helicopters.Mi_8MTV2
        AH_1W = helicopters.AH_1W
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.UH_60A,
        Helicopter.Mi_8MT,
        Helicopter.AH_1W,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        FFG_7CL_Oliver_Hazzard_Perry = ships.FFG_7CL_Oliver_Hazzard_Perry

    def __init__(self):
        super(Turkey, self).__init__(Turkey.id, Turkey.name)


class UK(Country):
    id = 4
    name = "UK"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            IFV_MCV_80 = vehicles.Armor.IFV_MCV_80
            MBT_Challenger_II = vehicles.Armor.MBT_Challenger_II
            TPz_Fuchs = vehicles.Armor.TPz_Fuchs
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            MLRS_M270 = vehicles.Artillery.MLRS_M270

        class AirDefence:
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        Tornado_GR4 = planes.Tornado_GR4
        C_130 = planes.C_130
        P_51D = planes.P_51D
        FW_190D9 = planes.Fw_190_D_9
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MQ_9_Reaper = planes.MQ_9_Reaper
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        B_17G = planes.B_17G
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.Tornado_GR4,
        Plane.C_130,
        Plane.P_51D,
        Plane.FW_190D9,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MQ_9_Reaper,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.B_17G,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        AH_64A = helicopters.AH_64A
        AH_64D = helicopters.AH_64D
        CH_47D = helicopters.CH_47D
        UH_1H = helicopters.UH_1H
        Mi_8MT = helicopters.Mi_8MTV2
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.AH_64A,
        Helicopter.AH_64D,
        Helicopter.CH_47D,
        Helicopter.UH_1H,
        Helicopter.Mi_8MT,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    class CallsignAWACS:
        Solex = "Solex"
        Image = "Image"

    callsign = {
        "AWACS": [
            CallsignAWACS.Solex,
            CallsignAWACS.Image
        ],
    }

    def __init__(self):
        super(UK, self).__init__(UK.id, UK.name)


class France(Country):
    id = 5
    name = "France"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            MBT_Leclerc = vehicles.Armor.MBT_Leclerc
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            MLRS_M270 = vehicles.Artillery.MLRS_M270

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        Mirage_2000_5 = planes.Mirage_2000_5
        C_130 = planes.C_130
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MQ_9_Reaper = planes.MQ_9_Reaper
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.Mirage_2000_5,
        Plane.C_130,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MQ_9_Reaper,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    class CallsignAWACS:
        Cyrano = "Cyrano"
        Roxanne = "Roxanne"

    callsign = {
        "AWACS": [
            CallsignAWACS.Cyrano,
            CallsignAWACS.Roxanne
        ],
    }

    def __init__(self):
        super(France, self).__init__(France.id, France.name)


class Germany(Country):
    id = 6
    name = "Germany"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Tanker_M978_HEMTT = vehicles.Unarmed.Tanker_M978_HEMTT
            HEMTT_TFFT = vehicles.Unarmed.HEMTT_TFFT
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            IFV_Marder = vehicles.Armor.IFV_Marder
            TPz_Fuchs = vehicles.Armor.TPz_Fuchs
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            SAM_Patriot_STR_AN_MPQ_53 = vehicles.AirDefence.SAM_Patriot_STR_AN_MPQ_53
            SAM_Patriot_LN_M901 = vehicles.AirDefence.SAM_Patriot_LN_M901
            SAM_Patriot_AMG_AN_MRC_137 = vehicles.AirDefence.SAM_Patriot_AMG_AN_MRC_137
            SAM_Patriot_EPP_III = vehicles.AirDefence.SAM_Patriot_EPP_III
            SAM_Patriot_ECS_AN_MSQ_104 = vehicles.AirDefence.SAM_Patriot_ECS_AN_MSQ_104
            SAM_Patriot_ICC = vehicles.AirDefence.SAM_Patriot_ICC
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            SAM_Roland_ADS = vehicles.AirDefence.SAM_Roland_ADS
            SAM_Roland_EWR = vehicles.AirDefence.SAM_Roland_EWR
            SPAAA_Gepard = vehicles.AirDefence.SPAAA_Gepard
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        MiG_29G = planes.MiG_29G
        F_4E = planes.F_4E
        Tornado_IDS = planes.Tornado_IDS
        P_51D = planes.P_51D
        FW_190D9 = planes.Fw_190_D_9
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.MiG_29G,
        Plane.F_4E,
        Plane.Tornado_IDS,
        Plane.P_51D,
        Plane.FW_190D9,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Germany, self).__init__(Germany.id, Germany.name)


class USAFAggressors(Country):
    id = 7
    name = "USAF Aggressors"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98
            Paratrooper_RPG_16 = vehicles.Infantry.Paratrooper_RPG_16
            Paratrooper_AKS = vehicles.Infantry.Paratrooper_AKS
            Infantry_Soldier_Rus = vehicles.Infantry.Infantry_Soldier_Rus
            Georgian_soldier_with_M4 = vehicles.Infantry.Georgian_soldier_with_M4
            Soldier_RPG = vehicles.Infantry.Soldier_RPG
            Soldier_AK = vehicles.Infantry.Soldier_AK
            Infantry_Soldier_Insurgents = vehicles.Infantry.Infantry_Soldier_Insurgents
            Infantry_M4 = vehicles.Infantry.Infantry_M4
            Soldier_M249 = vehicles.Infantry.Soldier_M249
            Infantry_M1_Garand = vehicles.Infantry.Infantry_M1_Garand

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Tanker_M978_HEMTT = vehicles.Unarmed.Tanker_M978_HEMTT
            HEMTT_TFFT = vehicles.Unarmed.HEMTT_TFFT
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_Ural_4320_31_Armored = vehicles.Unarmed.Transport_Ural_4320_31_Armored
            APC_Tigr_233036 = vehicles.Unarmed.APC_Tigr_233036
            Transport_KrAZ_6322 = vehicles.Unarmed.Transport_KrAZ_6322
            CP_Predator_GCS = vehicles.Unarmed.CP_Predator_GCS
            CP_Predator_TrojanSpirit = vehicles.Unarmed.CP_Predator_TrojanSpirit

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55
            APC_M113 = vehicles.Armor.APC_M113
            APC_AAV_7 = vehicles.Armor.APC_AAV_7
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            MBT_M60A3_Patton = vehicles.Armor.MBT_M60A3_Patton
            MBT_T_80U = vehicles.Armor.MBT_T_80U
            IFV_BMP_3 = vehicles.Armor.IFV_BMP_3
            ARV_MTLB_U_BOMAN = vehicles.Armor.ARV_MTLB_U_BOMAN
            MBT_T_90 = vehicles.Armor.MBT_T_90
            TPz_Fuchs = vehicles.Armor.TPz_Fuchs
            MBT_Merkava_Mk__4 = vehicles.Armor.MBT_Merkava_Mk__4
            IFV_Marder = vehicles.Armor.IFV_Marder
            MBT_Leclerc = vehicles.Armor.MBT_Leclerc
            MBT_M1A2_Abrams = vehicles.Armor.MBT_M1A2_Abrams
            IFV_LAV_25 = vehicles.Armor.IFV_LAV_25
            APC_Cobra = vehicles.Armor.APC_Cobra
            IFV_M2A2_Bradley = vehicles.Armor.IFV_M2A2_Bradley
            APC_M1126_Stryker_ICV = vehicles.Armor.APC_M1126_Stryker_ICV
            SPG_M1128_Stryker_MGS = vehicles.Armor.SPG_M1128_Stryker_MGS
            ATGM_M1134_Stryker = vehicles.Armor.ATGM_M1134_Stryker
            APC_M1043_HMMWV_Armament = vehicles.Armor.APC_M1043_HMMWV_Armament
            ATGM_M1045_HMMWV_TOW = vehicles.Armor.ATGM_M1045_HMMWV_TOW
            IFV_MCV_80 = vehicles.Armor.IFV_MCV_80
            MBT_Challenger_II = vehicles.Armor.MBT_Challenger_II

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            _2B11_mortar = vehicles.Artillery._2B11_mortar
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270
            SPH_2S19_Msta = vehicles.Artillery.SPH_2S19_Msta
            MLRS_9K57_Uragan_BM_27 = vehicles.Artillery.MLRS_9K57_Uragan_BM_27
            MLRS_9A52_Smerch = vehicles.Artillery.MLRS_9A52_Smerch
            SpGH_Dana = vehicles.Artillery.SpGH_Dana

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_18_Igla_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_MANPADS
            SAM_SA_18_Igla_comm = vehicles.AirDefence.SAM_SA_18_Igla_comm
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            SAM_Roland_ADS = vehicles.AirDefence.SAM_Roland_ADS
            SAM_Roland_EWR = vehicles.AirDefence.SAM_Roland_EWR
            EWR_1L13 = vehicles.AirDefence.EWR_1L13
            EWR_55G6 = vehicles.AirDefence.EWR_55G6
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_6_Kub_STR_9S91 = vehicles.AirDefence.SAM_SA_6_Kub_STR_9S91
            SAM_SA_6_Kub_LN_2P25 = vehicles.AirDefence.SAM_SA_6_Kub_LN_2P25
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6
            SAM_SA_18_Igla_S_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_S_MANPADS
            SAM_SA_18_Igla_S_comm = vehicles.AirDefence.SAM_SA_18_Igla_S_comm
            SAM_SA_3_S_125_LN_5P73 = vehicles.AirDefence.SAM_SA_3_S_125_LN_5P73
            SAM_SA_3_S_125_TR_SNR = vehicles.AirDefence.SAM_SA_3_S_125_TR_SNR
            SAM_SA_3_S_125_SR_P_19 = vehicles.AirDefence.SAM_SA_3_S_125_SR_P_19
            SAM_Avenger_M1097 = vehicles.AirDefence.SAM_Avenger_M1097
            SAM_Patriot_STR_AN_MPQ_53 = vehicles.AirDefence.SAM_Patriot_STR_AN_MPQ_53
            SAM_Patriot_LN_M901 = vehicles.AirDefence.SAM_Patriot_LN_M901
            SAM_Patriot_AMG_AN_MRC_137 = vehicles.AirDefence.SAM_Patriot_AMG_AN_MRC_137
            SAM_Patriot_EPP_III = vehicles.AirDefence.SAM_Patriot_EPP_III
            SAM_Patriot_ECS_AN_MSQ_104 = vehicles.AirDefence.SAM_Patriot_ECS_AN_MSQ_104
            SAM_Patriot_ICC = vehicles.AirDefence.SAM_Patriot_ICC
            AAA_Vulcan_M163 = vehicles.AirDefence.AAA_Vulcan_M163
            SAM_Chaparral_M48 = vehicles.AirDefence.SAM_Chaparral_M48
            SAM_Stinger_comm_dsr = vehicles.AirDefence.SAM_Stinger_comm_dsr
            SPAAA_Gepard = vehicles.AirDefence.SPAAA_Gepard
            AAA_ZU_23_Insurgent = vehicles.AirDefence.AAA_ZU_23_Insurgent
            AAA_ZU_23_Insurgent_Closed = vehicles.AirDefence.AAA_ZU_23_Insurgent_Closed
            AAA_ZU_23_Insurgent_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_Insurgent_on_Ural_375
            SAM_SA_18_Igla_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_MANPADS
            SAM_Linebacker_M6 = vehicles.AirDefence.SAM_Linebacker_M6

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        C_130 = planes.C_130
        F_16A_MLU = planes.F_16A_MLU
        P_51D = planes.P_51D
        Tornado_IDS = planes.Tornado_IDS
        MQ_9_Reaper = planes.MQ_9_Reaper
        TF_51D = planes.TF_51D
        F_A_18C = planes.F_A_18C
        Su_33 = planes.Su_33
        Su_25 = planes.Su_25
        MiG_29S = planes.MiG_29S
        MiG_29A = planes.MiG_29A
        Su_27 = planes.Su_27
        Su_25TM = planes.Su_25TM
        Su_25T = planes.Su_25T
        MiG_31 = planes.MiG_31
        MiG_27K = planes.MiG_27K
        Su_30 = planes.Su_30
        Tu_160 = planes.Tu_160
        Su_34 = planes.Su_34
        Tu_95MS = planes.Tu_95MS
        Tu_142 = planes.Tu_142
        MiG_25PD = planes.MiG_25PD
        Tu_22M3 = planes.Tu_22M3
        A_50 = planes.A_50
        Yak_40 = planes.Yak_40
        An_26B = planes.An_26B
        An_30M = planes.An_30M
        Su_17M4 = planes.Su_17M4
        MiG_23MLD = planes.MiG_23MLD
        MiG_25RBT = planes.MiG_25RBT
        Su_24M = planes.Su_24M
        Su_24MR = planes.Su_24MR
        IL_78M = planes.IL_78M
        IL_76MD = planes.IL_76MD
        L_39ZA = planes.L_39ZA
        FW_190D9 = planes.Fw_190_D_9
        F_15C = planes.F_15C
        F_15E = planes.F_15E
        F_16C_bl_52d = planes.F_16C_bl_52d
        F_4E = planes.F_4E
        MiG_29G = planes.MiG_29G
        Mirage_2000_5 = planes.Mirage_2000_5
        A_10A = planes.A_10A
        F_117A = planes.F_117A
        C_17A = planes.C_17A
        B_1B = planes.B_1B
        B_52H = planes.B_52H
        E_3A = planes.E_3A
        KC_135 = planes.KC_135
        F_14A = planes.F_14A
        S_3B = planes.S_3B
        S_3B_Tanker = planes.S_3B_Tanker
        E_2C = planes.E_2D
        F_16A = planes.F_16A
        RQ_1A_Predator = planes.MQ_1A_Predator
        B_17G = planes.B_17G
        Tornado_GR4 = planes.Tornado_GR4
        F_16C_bl_50 = planes.F_16C_bl_50

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.C_130,
        Plane.F_16A_MLU,
        Plane.P_51D,
        Plane.Tornado_IDS,
        Plane.MQ_9_Reaper,
        Plane.TF_51D,
        Plane.F_A_18C,
        Plane.Su_33,
        Plane.Su_25,
        Plane.MiG_29S,
        Plane.MiG_29A,
        Plane.Su_27,
        Plane.Su_25TM,
        Plane.Su_25T,
        Plane.MiG_31,
        Plane.MiG_27K,
        Plane.Su_30,
        Plane.Tu_160,
        Plane.Su_34,
        Plane.Tu_95MS,
        Plane.Tu_142,
        Plane.MiG_25PD,
        Plane.Tu_22M3,
        Plane.A_50,
        Plane.Yak_40,
        Plane.An_26B,
        Plane.An_30M,
        Plane.Su_17M4,
        Plane.MiG_23MLD,
        Plane.MiG_25RBT,
        Plane.Su_24M,
        Plane.Su_24MR,
        Plane.IL_78M,
        Plane.IL_76MD,
        Plane.L_39ZA,
        Plane.FW_190D9,
        Plane.F_15C,
        Plane.F_15E,
        Plane.F_16C_bl_52d,
        Plane.F_4E,
        Plane.MiG_29G,
        Plane.Mirage_2000_5,
        Plane.A_10A,
        Plane.F_117A,
        Plane.C_17A,
        Plane.B_1B,
        Plane.B_52H,
        Plane.E_3A,
        Plane.KC_135,
        Plane.F_14A,
        Plane.S_3B,
        Plane.S_3B_Tanker,
        Plane.E_2C,
        Plane.F_16A,
        Plane.RQ_1A_Predator,
        Plane.B_17G,
        Plane.Tornado_GR4,
        Plane.F_16C_bl_50,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        CH_47D = helicopters.CH_47D
        Mi_26 = helicopters.Mi_26
        Ka_27 = helicopters.Ka_27
        Mi_28N = helicopters.Mi_28N
        AH_64A = helicopters.AH_64A
        AH_1W = helicopters.AH_1W
        UH_60A = helicopters.UH_60A
        AH_64D = helicopters.AH_64D
        SH_60B = helicopters.SH_60B
        CH_53E = helicopters.CH_53E
        OH_58D = helicopters.OH_58D

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.CH_47D,
        Helicopter.Mi_26,
        Helicopter.Ka_27,
        Helicopter.Mi_28N,
        Helicopter.AH_64A,
        Helicopter.AH_1W,
        Helicopter.UH_60A,
        Helicopter.AH_64D,
        Helicopter.SH_60B,
        Helicopter.CH_53E,
        Helicopter.OH_58D,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase
        CV_1143_5_Admiral_Kuznetsov = ships.CV_1143_5_Admiral_Kuznetsov
        CG_1164_Moskva = ships.CG_1164_Moskva
        CGN_1144_2_Pyotr_Velikiy = ships.CGN_1144_2_Pyotr_Velikiy
        Tanker_Elnya_160 = ships.Tanker_Elnya_160
        FFL_1124_4_Grisha = ships.FFL_1124_4_Grisha
        FF_1135M_Rezky = ships.FF_1135M_Rezky
        FSG_1241_1MP_Molniya = ships.FSG_1241_1MP_Molniya
        SSK_877 = ships.SSK_877
        SSK_641B = ships.SSK_641B
        Civil_boat_Zvezdny = ships.Civil_boat_Zvezdny
        FFG_11540_Neustrashimy = ships.FFG_11540_Neustrashimy
        Bulk_cargo_ship_Yakushev = ships.Bulk_cargo_ship_Yakushev
        Dry_cargo_ship_Ivanov = ships.Dry_cargo_ship_Ivanov
        CVN_70_Carl_Vinson = ships.CVN_70_Carl_Vinson
        FFG_7CL_Oliver_Hazzard_Perry = ships.FFG_7CL_Oliver_Hazzard_Perry
        CG_60_Normandy = ships.CG_60_Normandy

    def __init__(self):
        super(USAFAggressors, self).__init__(USAFAggressors.id, USAFAggressors.name)


class Canada(Country):
    id = 8
    name = "Canada"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Tanker_M978_HEMTT = vehicles.Unarmed.Tanker_M978_HEMTT
            HEMTT_TFFT = vehicles.Unarmed.HEMTT_TFFT
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            IFV_LAV_25 = vehicles.Armor.IFV_LAV_25
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin

        class AirDefence:
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        P_51D = planes.P_51D
        F_A_18C = planes.F_A_18C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.P_51D,
        Plane.F_A_18C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(Canada, self).__init__(Canada.id, Canada.name)


class Spain(Country):
    id = 9
    name = "Spain"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            MBT_M60A3_Patton = vehicles.Armor.MBT_M60A3_Patton

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            SAM_Roland_ADS = vehicles.AirDefence.SAM_Roland_ADS
            SAM_Roland_EWR = vehicles.AirDefence.SAM_Roland_EWR

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        P_51D = planes.P_51D
        F_A_18C = planes.F_A_18C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.P_51D,
        Plane.F_A_18C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        CH_47D = helicopters.CH_47D
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.CH_47D,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Spain, self).__init__(Spain.id, Spain.name)


class TheNetherlands(Country):
    id = 10
    name = "The Netherlands"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            TPz_Fuchs = vehicles.Armor.TPz_Fuchs
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin

        class AirDefence:
            SAM_Patriot_STR_AN_MPQ_53 = vehicles.AirDefence.SAM_Patriot_STR_AN_MPQ_53
            SAM_Patriot_LN_M901 = vehicles.AirDefence.SAM_Patriot_LN_M901
            SAM_Patriot_AMG_AN_MRC_137 = vehicles.AirDefence.SAM_Patriot_AMG_AN_MRC_137
            SAM_Patriot_EPP_III = vehicles.AirDefence.SAM_Patriot_EPP_III
            SAM_Patriot_ECS_AN_MSQ_104 = vehicles.AirDefence.SAM_Patriot_ECS_AN_MSQ_104
            SAM_Patriot_ICC = vehicles.AirDefence.SAM_Patriot_ICC
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        F_16A_MLU = planes.F_16A_MLU
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.F_16A_MLU,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        AH_64A = helicopters.AH_64A
        AH_64D = helicopters.AH_64D
        CH_47D = helicopters.CH_47D
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.AH_64A,
        Helicopter.AH_64D,
        Helicopter.CH_47D,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(TheNetherlands, self).__init__(TheNetherlands.id, TheNetherlands.name)


class Belgium(Country):
    id = 11
    name = "Belgium"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        F_16A_MLU = planes.F_16A_MLU
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.F_16A_MLU,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(Belgium, self).__init__(Belgium.id, Belgium.name)


class Norway(Country):
    id = 12
    name = "Norway"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            TPz_Fuchs = vehicles.Armor.TPz_Fuchs

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        F_16A_MLU = planes.F_16A_MLU
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.F_16A_MLU,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Norway, self).__init__(Norway.id, Norway.name)


class Denmark(Country):
    id = 13
    name = "Denmark"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        F_16A_MLU = planes.F_16A_MLU
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.F_16A_MLU,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Denmark, self).__init__(Denmark.id, Denmark.name)


class Israel(Country):
    id = 15
    name = "Israel"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            TPz_Fuchs = vehicles.Armor.TPz_Fuchs
            MBT_M60A3_Patton = vehicles.Armor.MBT_M60A3_Patton
            MBT_T_55 = vehicles.Armor.MBT_T_55
            MBT_Merkava_Mk__4 = vehicles.Armor.MBT_Merkava_Mk__4

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270

        class AirDefence:
            SAM_Avenger_M1097 = vehicles.AirDefence.SAM_Avenger_M1097
            SAM_Patriot_STR_AN_MPQ_53 = vehicles.AirDefence.SAM_Patriot_STR_AN_MPQ_53
            SAM_Patriot_LN_M901 = vehicles.AirDefence.SAM_Patriot_LN_M901
            SAM_Patriot_AMG_AN_MRC_137 = vehicles.AirDefence.SAM_Patriot_AMG_AN_MRC_137
            SAM_Patriot_EPP_III = vehicles.AirDefence.SAM_Patriot_EPP_III
            SAM_Patriot_ECS_AN_MSQ_104 = vehicles.AirDefence.SAM_Patriot_ECS_AN_MSQ_104
            SAM_Patriot_ICC = vehicles.AirDefence.SAM_Patriot_ICC
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            AAA_Vulcan_M163 = vehicles.AirDefence.AAA_Vulcan_M163
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            SAM_Chaparral_M48 = vehicles.AirDefence.SAM_Chaparral_M48
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm_dsr = vehicles.AirDefence.SAM_Stinger_comm_dsr
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed

    class Plane:
        A_10C = planes.A_10C
        F_15C = planes.F_15C
        F_15E = planes.F_15E
        F_16C_bl_52d = planes.F_16C_bl_52d
        C_130 = planes.C_130
        F_4E = planes.F_4E
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.F_15C,
        Plane.F_15E,
        Plane.F_16C_bl_52d,
        Plane.C_130,
        Plane.F_4E,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        AH_64A = helicopters.AH_64A
        AH_1W = helicopters.AH_1W
        UH_60A = helicopters.UH_60A
        AH_64D = helicopters.AH_64D
        UH_1H = helicopters.UH_1H
        Mi_8MT = helicopters.Mi_8MTV2
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.AH_64A,
        Helicopter.AH_1W,
        Helicopter.UH_60A,
        Helicopter.AH_64D,
        Helicopter.UH_1H,
        Helicopter.Mi_8MT,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Israel, self).__init__(Israel.id, Israel.name)


class Georgia(Country):
    id = 16
    name = "Georgia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Georgian_soldier_with_M4 = vehicles.Infantry.Georgian_soldier_with_M4
            Soldier_RPG = vehicles.Infantry.Soldier_RPG

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Transport_KrAZ_6322 = vehicles.Unarmed.Transport_KrAZ_6322

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55
            APC_Cobra = vehicles.Armor.APC_Cobra

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S19_Msta = vehicles.Artillery.SPH_2S19_Msta
            SpGH_Dana = vehicles.Artillery.SpGH_Dana
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            EWR_1L13 = vehicles.AirDefence.EWR_1L13
            SAM_SA_18_Igla_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_MANPADS
            SAM_SA_18_Igla_comm = vehicles.AirDefence.SAM_SA_18_Igla_comm
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            SAM_SA_3_S_125_LN_5P73 = vehicles.AirDefence.SAM_SA_3_S_125_LN_5P73
            SAM_SA_3_S_125_TR_SNR = vehicles.AirDefence.SAM_SA_3_S_125_TR_SNR
            SAM_SA_3_S_125_SR_P_19 = vehicles.AirDefence.SAM_SA_3_S_125_SR_P_19

    class Plane:
        A_10C = planes.A_10C
        Su_25 = planes.Su_25
        An_26B = planes.An_26B
        Su_25T = planes.Su_25T
        L_39ZA = planes.L_39ZA
        Yak_40 = planes.Yak_40
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.Su_25,
        Plane.An_26B,
        Plane.Su_25T,
        Plane.L_39ZA,
        Plane.Yak_40,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        UH_1H = helicopters.UH_1H
        Mi_8MT = helicopters.Mi_8MTV2
        Mi_24V = helicopters.Mi_24V
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.UH_1H,
        Helicopter.Mi_8MT,
        Helicopter.Mi_24V,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        Tanker_Elnya_160 = ships.Tanker_Elnya_160
        FFL_1124_4_Grisha = ships.FFL_1124_4_Grisha
        FSG_1241_1MP_Molniya = ships.FSG_1241_1MP_Molniya
        Bulk_cargo_ship_Yakushev = ships.Bulk_cargo_ship_Yakushev
        Dry_cargo_ship_Ivanov = ships.Dry_cargo_ship_Ivanov
        Civil_boat_Zvezdny = ships.Civil_boat_Zvezdny

    def __init__(self):
        super(Georgia, self).__init__(Georgia.id, Georgia.name)


class Insurgents(Country):
    id = 17
    name = "Insurgents"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Soldier_AK = vehicles.Infantry.Soldier_AK
            Infantry_Soldier_Insurgents = vehicles.Infantry.Infantry_Soldier_Insurgents
            Soldier_RPG = vehicles.Infantry.Soldier_RPG

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_55 = vehicles.Armor.MBT_T_55

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            AAA_ZU_23_Insurgent = vehicles.AirDefence.AAA_ZU_23_Insurgent
            AAA_ZU_23_Insurgent_Closed = vehicles.AirDefence.AAA_ZU_23_Insurgent_Closed
            AAA_ZU_23_Insurgent_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_Insurgent_on_Ural_375
            SAM_SA_18_Igla_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_MANPADS
            SAM_SA_18_Igla_comm = vehicles.AirDefence.SAM_SA_18_Igla_comm
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm

    class Plane:
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        Tanker_Elnya_160 = ships.Tanker_Elnya_160
        FSG_1241_1MP_Molniya = ships.FSG_1241_1MP_Molniya
        Bulk_cargo_ship_Yakushev = ships.Bulk_cargo_ship_Yakushev
        Dry_cargo_ship_Ivanov = ships.Dry_cargo_ship_Ivanov
        Civil_boat_Zvezdny = ships.Civil_boat_Zvezdny

    def __init__(self):
        super(Insurgents, self).__init__(Insurgents.id, Insurgents.name)


class Abkhazia(Country):
    id = 18
    name = "Abkhazia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_6_Kub_STR_9S91 = vehicles.AirDefence.SAM_SA_6_Kub_STR_9S91
            SAM_SA_6_Kub_LN_2P25 = vehicles.AirDefence.SAM_SA_6_Kub_LN_2P25
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_18_Igla_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_MANPADS
            SAM_SA_18_Igla_comm = vehicles.AirDefence.SAM_SA_18_Igla_comm

    class Plane:
        Su_25 = planes.Su_25
        An_26B = planes.An_26B
        L_39ZA = planes.L_39ZA
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.Su_25,
        Plane.An_26B,
        Plane.L_39ZA,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        Ka_50 = helicopters.Ka_50
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.Ka_50,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        Tanker_Elnya_160 = ships.Tanker_Elnya_160
        FSG_1241_1MP_Molniya = ships.FSG_1241_1MP_Molniya
        Civil_boat_Zvezdny = ships.Civil_boat_Zvezdny
        Bulk_cargo_ship_Yakushev = ships.Bulk_cargo_ship_Yakushev
        Dry_cargo_ship_Ivanov = ships.Dry_cargo_ship_Ivanov

    def __init__(self):
        super(Abkhazia, self).__init__(Abkhazia.id, Abkhazia.name)


class SouthOssetia(Country):
    id = 19
    name = "South Ossetia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_18_Igla_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_MANPADS
            SAM_SA_18_Igla_comm = vehicles.AirDefence.SAM_SA_18_Igla_comm

    class Plane:
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        Ka_50 = helicopters.Ka_50
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.Ka_50,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    def __init__(self):
        super(SouthOssetia, self).__init__(SouthOssetia.id, SouthOssetia.name)


class Italy(Country):
    id = 20
    name = "Italy"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818
            Tanker_M978_HEMTT = vehicles.Unarmed.Tanker_M978_HEMTT
            HEMTT_TFFT = vehicles.Unarmed.HEMTT_TFFT

        class Armor:
            APC_M113 = vehicles.Armor.APC_M113
            APC_AAV_7 = vehicles.Armor.APC_AAV_7
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        F_16A_MLU = planes.F_16A_MLU
        P_51D = planes.P_51D
        Tornado_IDS = planes.Tornado_IDS
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MQ_9_Reaper = planes.MQ_9_Reaper
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.F_16A_MLU,
        Plane.P_51D,
        Plane.Tornado_IDS,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MQ_9_Reaper,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Italy, self).__init__(Italy.id, Italy.name)


class Australia(Country):
    id = 21
    name = "Australia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            MBT_M1A2_Abrams = vehicles.Armor.MBT_M1A2_Abrams
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            IFV_LAV_25 = vehicles.Armor.IFV_LAV_25
            APC_M113 = vehicles.Armor.APC_M113
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class AirDefence:
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        P_51D = planes.P_51D
        F_A_18C = planes.F_A_18C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis
        TF_51D = planes.TF_51D

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.P_51D,
        Plane.F_A_18C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
        Plane.TF_51D,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        CH_47D = helicopters.CH_47D
        UH_1H = helicopters.UH_1H
        UH_60A = helicopters.UH_60A
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.CH_47D,
        Helicopter.UH_1H,
        Helicopter.UH_60A,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(Australia, self).__init__(Australia.id, Australia.name)


class Switzerland(Country):
    id = 22
    name = "Switzerland"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Armor:
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2
            APC_M113 = vehicles.Armor.APC_M113

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin

        class AirDefence:
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm

    class Plane:
        A_10C = planes.A_10C
        F_A_18C = planes.F_A_18C
        P_51D = planes.P_51D
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.F_A_18C,
        Plane.P_51D,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Switzerland, self).__init__(Switzerland.id, Switzerland.name)


class Austria(Country):
    id = 23
    name = "Austria"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Austria, self).__init__(Austria.id, Austria.name)


class Belarus(Country):
    id = 24
    name = "Belarus"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Paratrooper_RPG_16 = vehicles.Infantry.Paratrooper_RPG_16
            Paratrooper_AKS = vehicles.Infantry.Paratrooper_AKS
            Infantry_Soldier_Rus = vehicles.Infantry.Infantry_Soldier_Rus

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_Ural_4320_31_Armored = vehicles.Unarmed.Transport_Ural_4320_31_Armored
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            IFV_BMP_3 = vehicles.Armor.IFV_BMP_3
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55
            ARV_MTLB_U_BOMAN = vehicles.Armor.ARV_MTLB_U_BOMAN

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S19_Msta = vehicles.Artillery.SPH_2S19_Msta
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            MLRS_9K57_Uragan_BM_27 = vehicles.Artillery.MLRS_9K57_Uragan_BM_27
            MLRS_9A52_Smerch = vehicles.Artillery.MLRS_9A52_Smerch
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            EWR_1L13 = vehicles.AirDefence.EWR_1L13
            EWR_55G6 = vehicles.AirDefence.EWR_55G6
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_6_Kub_STR_9S91 = vehicles.AirDefence.SAM_SA_6_Kub_STR_9S91
            SAM_SA_6_Kub_LN_2P25 = vehicles.AirDefence.SAM_SA_6_Kub_LN_2P25
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_18_Igla_S_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_S_MANPADS
            SAM_SA_18_Igla_S_comm = vehicles.AirDefence.SAM_SA_18_Igla_S_comm
            SAM_SA_3_S_125_LN_5P73 = vehicles.AirDefence.SAM_SA_3_S_125_LN_5P73
            SAM_SA_3_S_125_TR_SNR = vehicles.AirDefence.SAM_SA_3_S_125_TR_SNR
            SAM_SA_3_S_125_SR_P_19 = vehicles.AirDefence.SAM_SA_3_S_125_SR_P_19

    class Plane:
        A_10C = planes.A_10C
        Su_25 = planes.Su_25
        MiG_29S = planes.MiG_29S
        MiG_29A = planes.MiG_29A
        Su_27 = planes.Su_27
        Yak_40 = planes.Yak_40
        An_26B = planes.An_26B
        An_30M = planes.An_30M
        Su_24M = planes.Su_24M
        Su_24MR = planes.Su_24MR
        IL_76MD = planes.IL_76MD
        L_39C = planes.L_39C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Su_25,
        Plane.MiG_29S,
        Plane.MiG_29A,
        Plane.Su_27,
        Plane.Yak_40,
        Plane.An_26B,
        Plane.An_30M,
        Plane.Su_24M,
        Plane.Su_24MR,
        Plane.IL_76MD,
        Plane.L_39C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        Mi_26 = helicopters.Mi_26
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.Mi_26,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Belarus, self).__init__(Belarus.id, Belarus.name)


class Bulgaria(Country):
    id = 25
    name = "Bulgaria"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        L_39ZA = planes.L_39ZA
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.L_39ZA,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Bulgaria, self).__init__(Bulgaria.id, Bulgaria.name)


class CzechRepublic(Country):
    id = 26
    name = "Czech Republic"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SpGH_Dana = vehicles.Artillery.SpGH_Dana

        class AirDefence:
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        L_39ZA = planes.L_39ZA
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.L_39ZA,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(CzechRepublic, self).__init__(CzechRepublic.id, CzechRepublic.name)


class China(Country):
    id = 27
    name = "China"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class AirDefence:
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6

    class Plane:
        A_10C = planes.A_10C
        Su_27 = planes.Su_27
        IL_76MD = planes.IL_76MD
        IL_78M = planes.IL_78M
        An_26B = planes.An_26B
        An_30M = planes.An_30M
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Su_27,
        Plane.IL_76MD,
        Plane.IL_78M,
        Plane.An_26B,
        Plane.An_30M,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_8MT = helicopters.Mi_8MTV2
        Mi_26 = helicopters.Mi_26
        Ka_27 = helicopters.Ka_27
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_8MT,
        Helicopter.Mi_26,
        Helicopter.Ka_27,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(China, self).__init__(China.id, China.name)


class Croatia(Country):
    id = 28
    name = "Croatia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Croatia, self).__init__(Croatia.id, Croatia.name)


class Egypt(Country):
    id = 29
    name = "Egypt"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Egypt, self).__init__(Egypt.id, Egypt.name)


class Finland(Country):
    id = 30
    name = "Finland"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Finland, self).__init__(Finland.id, Finland.name)


class Greece(Country):
    id = 31
    name = "Greece"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_M4 = vehicles.Infantry.Infantry_M4
            Soldier_M249 = vehicles.Infantry.Soldier_M249

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            APC_M1025_HMMWV = vehicles.Unarmed.APC_M1025_HMMWV
            Transport_M818 = vehicles.Unarmed.Transport_M818

        class Armor:
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            APC_M113 = vehicles.Armor.APC_M113
            APC_M1043_HMMWV_Armament = vehicles.Armor.APC_M1043_HMMWV_Armament
            ATGM_M1045_HMMWV_TOW = vehicles.Armor.ATGM_M1045_HMMWV_TOW
            MBT_Leopard_1A3 = vehicles.Armor.MBT_Leopard_1A3
            MBT_Leopard_2 = vehicles.Armor.MBT_Leopard_2

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_M109_Paladin = vehicles.Artillery.SPH_M109_Paladin
            MLRS_M270 = vehicles.Artillery.MLRS_M270

        class AirDefence:
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            Stinger_MANPADS = vehicles.AirDefence.Stinger_MANPADS
            SAM_Stinger_comm = vehicles.AirDefence.SAM_Stinger_comm
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            SAM_Patriot_AMG_AN_MRC_137 = vehicles.AirDefence.SAM_Patriot_AMG_AN_MRC_137
            SAM_Patriot_ECS_AN_MSQ_104 = vehicles.AirDefence.SAM_Patriot_ECS_AN_MSQ_104
            SAM_Patriot_LN_M901 = vehicles.AirDefence.SAM_Patriot_LN_M901
            SAM_Patriot_EPP_III = vehicles.AirDefence.SAM_Patriot_EPP_III
            SAM_Patriot_ICC = vehicles.AirDefence.SAM_Patriot_ICC
            SAM_Patriot_STR_AN_MPQ_53 = vehicles.AirDefence.SAM_Patriot_STR_AN_MPQ_53
            SAM_Hawk_TR_AN_MPQ_46 = vehicles.AirDefence.SAM_Hawk_TR_AN_MPQ_46
            SAM_Hawk_SR_AN_MPQ_50 = vehicles.AirDefence.SAM_Hawk_SR_AN_MPQ_50
            SAM_Hawk_LN_M192 = vehicles.AirDefence.SAM_Hawk_LN_M192
            SAM_Hawk_CWAR_AN_MPQ_55 = vehicles.AirDefence.SAM_Hawk_CWAR_AN_MPQ_55
            SAM_Hawk_PCP = vehicles.AirDefence.SAM_Hawk_PCP
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6

    class Plane:
        A_10C = planes.A_10C
        C_130 = planes.C_130
        F_4E = planes.F_4E
        F_16C_bl_50 = planes.F_16C_bl_50
        F_16C_bl_52d = planes.F_16C_bl_52d
        Mirage_2000_5 = planes.Mirage_2000_5
        Yak_40 = planes.Yak_40
        F_15C = planes.F_15C
        MiG_29A = planes.MiG_29A
        MiG_29S = planes.MiG_29S
        Su_33 = planes.Su_33
        Su_27 = planes.Su_27
        Su_25T = planes.Su_25T
        Su_25 = planes.Su_25
        P_51D = planes.P_51D
        TF_51D = planes.TF_51D
        A_10A = planes.A_10A
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.C_130,
        Plane.F_4E,
        Plane.F_16C_bl_50,
        Plane.F_16C_bl_52d,
        Plane.Mirage_2000_5,
        Plane.Yak_40,
        Plane.F_15C,
        Plane.MiG_29A,
        Plane.MiG_29S,
        Plane.Su_33,
        Plane.Su_27,
        Plane.Su_25T,
        Plane.Su_25,
        Plane.P_51D,
        Plane.TF_51D,
        Plane.A_10A,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        AH_64A = helicopters.AH_64A
        AH_64D = helicopters.AH_64D
        CH_47D = helicopters.CH_47D
        UH_1H = helicopters.UH_1H
        SH_60B = helicopters.SH_60B
        Mi_8MT = helicopters.Mi_8MTV2
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.AH_64A,
        Helicopter.AH_64D,
        Helicopter.CH_47D,
        Helicopter.UH_1H,
        Helicopter.SH_60B,
        Helicopter.Mi_8MT,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Greece, self).__init__(Greece.id, Greece.name)


class Hungary(Country):
    id = 32
    name = "Hungary"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        L_39ZA = planes.L_39ZA
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.L_39ZA,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Hungary, self).__init__(Hungary.id, Hungary.name)


class India(Country):
    id = 33
    name = "India"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(India, self).__init__(India.id, India.name)


class Iran(Country):
    id = 34
    name = "Iran"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Iran, self).__init__(Iran.id, Iran.name)


class Iraq(Country):
    id = 35
    name = "Iraq"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Iraq, self).__init__(Iraq.id, Iraq.name)


class Japan(Country):
    id = 36
    name = "Japan"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Japan, self).__init__(Japan.id, Japan.name)


class Kazakhstan(Country):
    id = 37
    name = "Kazakhstan"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Paratrooper_RPG_16 = vehicles.Infantry.Paratrooper_RPG_16
            Paratrooper_AKS = vehicles.Infantry.Paratrooper_AKS
            Infantry_Soldier_Rus = vehicles.Infantry.Infantry_Soldier_Rus

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Fuel_Truck_ATMZ_5 = vehicles.Unarmed.Fuel_Truck_ATMZ_5
            Fuel_Truck_ATZ_10 = vehicles.Unarmed.Fuel_Truck_ATZ_10
            Transport_UAZ_469 = vehicles.Unarmed.Transport_UAZ_469
            Transport_Ural_375 = vehicles.Unarmed.Transport_Ural_375
            CP_Ural_375_PBU = vehicles.Unarmed.CP_Ural_375_PBU
            Transport_IKARUS_280 = vehicles.Unarmed.Transport_IKARUS_280
            Transport_VAZ_2109 = vehicles.Unarmed.Transport_VAZ_2109
            Transport_ZIU_9 = vehicles.Unarmed.Transport_ZIU_9
            Transport_KAMAZ_43101 = vehicles.Unarmed.Transport_KAMAZ_43101
            Transport_LAZ_695 = vehicles.Unarmed.Transport_LAZ_695
            Transport_GAZ_3307 = vehicles.Unarmed.Transport_GAZ_3307
            Transport_GAZ_66 = vehicles.Unarmed.Transport_GAZ_66
            Transport_GAZ_3308 = vehicles.Unarmed.Transport_GAZ_3308
            Transport_MAZ_6303 = vehicles.Unarmed.Transport_MAZ_6303
            Transport_ZIL_4331 = vehicles.Unarmed.Transport_ZIL_4331
            CP_SKP_11_ATC_Mobile_Command_Post = vehicles.Unarmed.CP_SKP_11_ATC_Mobile_Command_Post
            Transport_Ural_4320T = vehicles.Unarmed.Transport_Ural_4320T
            Transport_Ural_4320_31_Armored = vehicles.Unarmed.Transport_Ural_4320_31_Armored
            Transport_fire_engine_Ural_ATsP_6 = vehicles.Unarmed.Transport_fire_engine_Ural_ATsP_6
            GPU_APA_80_on_ZiL_131 = vehicles.Unarmed.GPU_APA_80_on_ZiL_131
            Transport_ZIL_131_KUNG = vehicles.Unarmed.Transport_ZIL_131_KUNG
            GPU_APA_5D_on_Ural_4320 = vehicles.Unarmed.GPU_APA_5D_on_Ural_4320

        class Armor:
            APC_BTR_80 = vehicles.Armor.APC_BTR_80
            IFV_BMD_1 = vehicles.Armor.IFV_BMD_1
            IFV_BMP_1 = vehicles.Armor.IFV_BMP_1
            IFV_BMP_2 = vehicles.Armor.IFV_BMP_2
            ARV_BRDM_2 = vehicles.Armor.ARV_BRDM_2
            MBT_T_80U = vehicles.Armor.MBT_T_80U
            IFV_BMP_3 = vehicles.Armor.IFV_BMP_3
            ARV_BTR_RD = vehicles.Armor.ARV_BTR_RD
            APC_MTLB = vehicles.Armor.APC_MTLB
            MBT_T_72B = vehicles.Armor.MBT_T_72B
            MBT_T_55 = vehicles.Armor.MBT_T_55
            ARV_MTLB_U_BOMAN = vehicles.Armor.ARV_MTLB_U_BOMAN

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SPH_2S19_Msta = vehicles.Artillery.SPH_2S19_Msta
            SPH_2S3_Akatsia = vehicles.Artillery.SPH_2S3_Akatsia
            SPH_2S9_Nona = vehicles.Artillery.SPH_2S9_Nona
            MLRS_BM_21_Grad = vehicles.Artillery.MLRS_BM_21_Grad
            MLRS_9K57_Uragan_BM_27 = vehicles.Artillery.MLRS_9K57_Uragan_BM_27
            MLRS_9A52_Smerch = vehicles.Artillery.MLRS_9A52_Smerch
            SPH_2S1_Gvozdika = vehicles.Artillery.SPH_2S1_Gvozdika
            _2B11_mortar = vehicles.Artillery._2B11_mortar

        class AirDefence:
            EWR_1L13 = vehicles.AirDefence.EWR_1L13
            EWR_55G6 = vehicles.AirDefence.EWR_55G6
            SAM_SA_10_S_300PS_TR_30N6 = vehicles.AirDefence.SAM_SA_10_S_300PS_TR_30N6
            SAM_SA_10_S_300PS_SR_5N66M = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_5N66M
            SAM_SA_10_S_300PS_SR_64H6E = vehicles.AirDefence.SAM_SA_10_S_300PS_SR_64H6E
            SAM_SA_10_S_300PS_LN_5P85C = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85C
            SAM_SA_10_S_300PS_LN_5P85D = vehicles.AirDefence.SAM_SA_10_S_300PS_LN_5P85D
            SAM_SA_11_Buk_SR_9S18M1 = vehicles.AirDefence.SAM_SA_11_Buk_SR_9S18M1
            SAM_SA_11_Buk_CC_9S470M1 = vehicles.AirDefence.SAM_SA_11_Buk_CC_9S470M1
            SAM_SA_11_Buk_LN_9A310M1 = vehicles.AirDefence.SAM_SA_11_Buk_LN_9A310M1
            SAM_SA_6_Kub_STR_9S91 = vehicles.AirDefence.SAM_SA_6_Kub_STR_9S91
            SAM_SA_6_Kub_LN_2P25 = vehicles.AirDefence.SAM_SA_6_Kub_LN_2P25
            SAM_SA_8_Osa_9A33 = vehicles.AirDefence.SAM_SA_8_Osa_9A33
            SAM_SA_9_Strela_1_9P31 = vehicles.AirDefence.SAM_SA_9_Strela_1_9P31
            SAM_SA_13_Strela_10M3_9A35M3 = vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3
            CP_9S80M1_Sborka = vehicles.AirDefence.CP_9S80M1_Sborka
            SAM_SA_15_Tor_9A331 = vehicles.AirDefence.SAM_SA_15_Tor_9A331
            SAM_SA_19_Tunguska_2S6 = vehicles.AirDefence.SAM_SA_19_Tunguska_2S6
            SPAAA_ZSU_23_4_Shilka = vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka
            SAM_SA_10_S_300PS_CP_54K6 = vehicles.AirDefence.SAM_SA_10_S_300PS_CP_54K6
            AAA_ZU_23_Emplacement = vehicles.AirDefence.AAA_ZU_23_Emplacement
            AAA_ZU_23_Closed = vehicles.AirDefence.AAA_ZU_23_Closed
            AAA_ZU_23_on_Ural_375 = vehicles.AirDefence.AAA_ZU_23_on_Ural_375
            SAM_SA_18_Igla_S_MANPADS = vehicles.AirDefence.SAM_SA_18_Igla_S_MANPADS
            SAM_SA_18_Igla_S_comm = vehicles.AirDefence.SAM_SA_18_Igla_S_comm
            SAM_SA_3_S_125_LN_5P73 = vehicles.AirDefence.SAM_SA_3_S_125_LN_5P73
            SAM_SA_3_S_125_TR_SNR = vehicles.AirDefence.SAM_SA_3_S_125_TR_SNR
            SAM_SA_3_S_125_SR_P_19 = vehicles.AirDefence.SAM_SA_3_S_125_SR_P_19

    class Plane:
        A_10C = planes.A_10C
        Su_25 = planes.Su_25
        MiG_29S = planes.MiG_29S
        MiG_29A = planes.MiG_29A
        Su_27 = planes.Su_27
        MiG_31 = planes.MiG_31
        Su_30 = planes.Su_30
        Yak_40 = planes.Yak_40
        An_26B = planes.An_26B
        An_30M = planes.An_30M
        Su_24M = planes.Su_24M
        Su_24MR = planes.Su_24MR
        IL_76MD = planes.IL_76MD
        L_39C = planes.L_39C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Su_25,
        Plane.MiG_29S,
        Plane.MiG_29A,
        Plane.Su_27,
        Plane.MiG_31,
        Plane.Su_30,
        Plane.Yak_40,
        Plane.An_26B,
        Plane.An_30M,
        Plane.Su_24M,
        Plane.Su_24MR,
        Plane.IL_76MD,
        Plane.L_39C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        Mi_24V = helicopters.Mi_24V
        Mi_8MT = helicopters.Mi_8MTV2
        Mi_26 = helicopters.Mi_26
        UH_1H = helicopters.UH_1H
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.Mi_24V,
        Helicopter.Mi_8MT,
        Helicopter.Mi_26,
        Helicopter.UH_1H,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Kazakhstan, self).__init__(Kazakhstan.id, Kazakhstan.name)


class NorthKorea(Country):
    id = 38
    name = "North Korea"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(NorthKorea, self).__init__(NorthKorea.id, NorthKorea.name)


class Pakistan(Country):
    id = 39
    name = "Pakistan"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Pakistan, self).__init__(Pakistan.id, Pakistan.name)


class Poland(Country):
    id = 40
    name = "Poland"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SpGH_Dana = vehicles.Artillery.SpGH_Dana

        class AirDefence:
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(Poland, self).__init__(Poland.id, Poland.name)


class Romania(Country):
    id = 41
    name = "Romania"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Romania, self).__init__(Romania.id, Romania.name)


class SaudiArabia(Country):
    id = 42
    name = "Saudi Arabia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(SaudiArabia, self).__init__(SaudiArabia.id, SaudiArabia.name)


class Serbia(Country):
    id = 43
    name = "Serbia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Serbia, self).__init__(Serbia.id, Serbia.name)


class Slovakia(Country):
    id = 44
    name = "Slovakia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SpGH_Dana = vehicles.Artillery.SpGH_Dana

    class Plane:
        A_10C = planes.A_10C
        L_39ZA = planes.L_39ZA
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.L_39ZA,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Slovakia, self).__init__(Slovakia.id, Slovakia.name)


class SouthKorea(Country):
    id = 45
    name = "South Korea"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(SouthKorea, self).__init__(SouthKorea.id, SouthKorea.name)


class Sweden(Country):
    id = 46
    name = "Sweden"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Sweden, self).__init__(Sweden.id, Sweden.name)


class Syria(Country):
    id = 47
    name = "Syria"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        L_39ZA = planes.L_39ZA
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis
        MiG_21Bis = planes.MiG_21Bis

    planes = [
        Plane.A_10C,
        Plane.L_39ZA,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
        Plane.MiG_21Bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Syria, self).__init__(Syria.id, Syria.name)


class Yemen(Country):
    id = 48
    name = "Yemen"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Yemen, self).__init__(Yemen.id, Yemen.name)


class Vietnam(Country):
    id = 49
    name = "Vietnam"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Vietnam, self).__init__(Vietnam.id, Vietnam.name)


class Venezuela(Country):
    id = 50
    name = "Venezuela"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Venezuela, self).__init__(Venezuela.id, Venezuela.name)


class Tunisia(Country):
    id = 51
    name = "Tunisia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Tunisia, self).__init__(Tunisia.id, Tunisia.name)


class Thailand(Country):
    id = 52
    name = "Thailand"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Thailand, self).__init__(Thailand.id, Thailand.name)


class Sudan(Country):
    id = 53
    name = "Sudan"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Sudan, self).__init__(Sudan.id, Sudan.name)


class Philippines(Country):
    id = 54
    name = "Philippines"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Philippines, self).__init__(Philippines.id, Philippines.name)


class Morocco(Country):
    id = 55
    name = "Morocco"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Morocco, self).__init__(Morocco.id, Morocco.name)


class Mexico(Country):
    id = 56
    name = "Mexico"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Mexico, self).__init__(Mexico.id, Mexico.name)


class Malaysia(Country):
    id = 57
    name = "Malaysia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Malaysia, self).__init__(Malaysia.id, Malaysia.name)


class Libya(Country):
    id = 58
    name = "Libya"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            SpGH_Dana = vehicles.Artillery.SpGH_Dana

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Libya, self).__init__(Libya.id, Libya.name)


class Jordan(Country):
    id = 59
    name = "Jordan"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Jordan, self).__init__(Jordan.id, Jordan.name)


class Indonesia(Country):
    id = 60
    name = "Indonesia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Indonesia, self).__init__(Indonesia.id, Indonesia.name)


class Honduras(Country):
    id = 61
    name = "Honduras"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Honduras, self).__init__(Honduras.id, Honduras.name)


class Ethiopia(Country):
    id = 62
    name = "Ethiopia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Ethiopia, self).__init__(Ethiopia.id, Ethiopia.name)


class Chile(Country):
    id = 63
    name = "Chile"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Chile, self).__init__(Chile.id, Chile.name)


class Brazil(Country):
    id = 64
    name = "Brazil"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Brazil, self).__init__(Brazil.id, Brazil.name)


class Bahrain(Country):
    id = 65
    name = "Bahrain"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(Bahrain, self).__init__(Bahrain.id, Bahrain.name)


class ThirdReich(Country):
    id = 66
    name = "Third Reich"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        FW_190D9 = planes.Fw_190_D_9
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.FW_190D9,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(ThirdReich, self).__init__(ThirdReich.id, ThirdReich.name)


class Yugoslavia(Country):
    id = 67
    name = "Yugoslavia"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class AirDefence:
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(Yugoslavia, self).__init__(Yugoslavia.id, Yugoslavia.name)


class USSR(Country):
    id = 68
    name = "USSR"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Bedford_MWD = vehicles.Unarmed.Bedford_MWD
            CCKW_353 = vehicles.Unarmed.CCKW_353
            Willys_MB = vehicles.Unarmed.Willys_MB

        class Armor:
            CT_Cromwell_IV = vehicles.Armor.CT_Cromwell_IV
            MT_M4A4_Sherman_Firefly = vehicles.Armor.MT_M4A4_Sherman_Firefly
            MT_M4_Sherman = vehicles.Armor.MT_M4_Sherman

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class AirDefence:
            AAA_Bofors_40mm = vehicles.AirDefence.AAA_Bofors_40mm

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat
        LST_Mk_II = ships.LST_Mk_II
        LS_Samuel_Chase = ships.LS_Samuel_Chase

    def __init__(self):
        super(USSR, self).__init__(USSR.id, USSR.name)


class ItalianSocialRepublic(Country):
    id = 69
    name = "Italian Social Republic"

    class Vehicle:

        class Fortification:
            Bunker_2 = vehicles.Fortification.Bunker_2
            Bunker_1 = vehicles.Fortification.Bunker_1
            Barracks_armed = vehicles.Fortification.Barracks_armed
            Watch_tower_armed = vehicles.Fortification.Watch_tower_armed
            Road_outpost = vehicles.Fortification.Road_outpost
            Outpost = vehicles.Fortification.Outpost
            Armed_house = vehicles.Fortification.Armed_house

        class Infantry:
            Infantry_Mauser_98 = vehicles.Infantry.Infantry_Mauser_98

        class Locomotive:
            DRG_Class_86 = vehicles.Locomotive.DRG_Class_86

        class Unarmed:
            Kübelwagen_82 = vehicles.Unarmed.Kübelwagen_82
            Blitz_3_6_6700A = vehicles.Unarmed.Blitz_3_6_6700A

        class Armor:
            HT_Pz_Kpfw_VI_Tiger_I = vehicles.Armor.HT_Pz_Kpfw_VI_Tiger_I
            HT_Pz_Kpfw_VI_Ausf__B__Tiger_II = vehicles.Armor.HT_Pz_Kpfw_VI_Ausf__B__Tiger_II
            MT_Pz_Kpfw_V_Panther_Ausf_G = vehicles.Armor.MT_Pz_Kpfw_V_Panther_Ausf_G
            MT_Pz_Kpfw_IV_Ausf_H = vehicles.Armor.MT_Pz_Kpfw_IV_Ausf_H
            Jagdpanther_G1 = vehicles.Armor.Jagdpanther_G1
            Jagdpanzer_IV = vehicles.Armor.Jagdpanzer_IV

        class Carriage:
            DR_50Ton_Flat_Wagon = vehicles.Carriage.DR_50Ton_Flat_Wagon
            German_covered_wagon_G10 = vehicles.Carriage.German_covered_wagon_G10
            German_tank_wagon = vehicles.Carriage.German_tank_wagon

        class Artillery:
            Sturmpanzer_IV_Brummbär = vehicles.Artillery.Sturmpanzer_IV_Brummbär
            SK_C_28_15cm_naval_gun = vehicles.Artillery.SK_C_28_15cm_naval_gun

        class AirDefence:
            AAA_Flak_18 = vehicles.AirDefence.AAA_Flak_18
            AAA_Flak_30 = vehicles.AirDefence.AAA_Flak_30
            AAA_Flak_36 = vehicles.AirDefence.AAA_Flak_36
            AAA_Flak_37 = vehicles.AirDefence.AAA_Flak_37
            AAA_Flak_Vierling_38 = vehicles.AirDefence.AAA_Flak_Vierling_38

    class Plane:
        A_10C = planes.A_10C
        Bf_109K_4 = planes.Bf_109_K_4
        Spitfire_LF_Mk__IX = planes.Spitfire_LF_Mk__IX
        AJS37 = planes.AJS37
        C_101EB = planes.C_101EB
        C_101CC = planes.C_101CC
        F_5E = planes.F_5E
        F_5E_3 = planes.F_5E_3
        F_86F_Sabre = planes.F_86F
        Hawk = planes.Hawk
        L_39C = planes.L_39C
        M_2000C = planes.M_2000C
        MiG_15bis = planes.MiG_15bis

    planes = [
        Plane.A_10C,
        Plane.Bf_109K_4,
        Plane.Spitfire_LF_Mk__IX,
        Plane.AJS37,
        Plane.C_101EB,
        Plane.C_101CC,
        Plane.F_5E,
        Plane.F_5E_3,
        Plane.F_86F_Sabre,
        Plane.Hawk,
        Plane.L_39C,
        Plane.M_2000C,
        Plane.MiG_15bis,
    ]

    class Helicopter:
        Ka_50 = helicopters.Ka_50
        SA342M = helicopters.SA342M
        SA342L = helicopters.SA342L
        SA342Mistral = helicopters.SA342Mistral

    helicopters = [
        Helicopter.Ka_50,
        Helicopter.SA342M,
        Helicopter.SA342L,
        Helicopter.SA342Mistral,
    ]

    class Ship:
        Armed_speedboat = ships.Armed_speedboat

    def __init__(self):
        super(ItalianSocialRepublic, self).__init__(ItalianSocialRepublic.id, ItalianSocialRepublic.name)

country_dict = {
    Russia.id: Russia,
    Ukraine.id: Ukraine,
    USA.id: USA,
    Turkey.id: Turkey,
    UK.id: UK,
    France.id: France,
    Germany.id: Germany,
    USAFAggressors.id: USAFAggressors,
    Canada.id: Canada,
    Spain.id: Spain,
    TheNetherlands.id: TheNetherlands,
    Belgium.id: Belgium,
    Norway.id: Norway,
    Denmark.id: Denmark,
    Israel.id: Israel,
    Georgia.id: Georgia,
    Insurgents.id: Insurgents,
    Abkhazia.id: Abkhazia,
    SouthOssetia.id: SouthOssetia,
    Italy.id: Italy,
    Australia.id: Australia,
    Switzerland.id: Switzerland,
    Austria.id: Austria,
    Belarus.id: Belarus,
    Bulgaria.id: Bulgaria,
    CzechRepublic.id: CzechRepublic,
    China.id: China,
    Croatia.id: Croatia,
    Egypt.id: Egypt,
    Finland.id: Finland,
    Greece.id: Greece,
    Hungary.id: Hungary,
    India.id: India,
    Iran.id: Iran,
    Iraq.id: Iraq,
    Japan.id: Japan,
    Kazakhstan.id: Kazakhstan,
    NorthKorea.id: NorthKorea,
    Pakistan.id: Pakistan,
    Poland.id: Poland,
    Romania.id: Romania,
    SaudiArabia.id: SaudiArabia,
    Serbia.id: Serbia,
    Slovakia.id: Slovakia,
    SouthKorea.id: SouthKorea,
    Sweden.id: Sweden,
    Syria.id: Syria,
    Yemen.id: Yemen,
    Vietnam.id: Vietnam,
    Venezuela.id: Venezuela,
    Tunisia.id: Tunisia,
    Thailand.id: Thailand,
    Sudan.id: Sudan,
    Philippines.id: Philippines,
    Morocco.id: Morocco,
    Mexico.id: Mexico,
    Malaysia.id: Malaysia,
    Libya.id: Libya,
    Jordan.id: Jordan,
    Indonesia.id: Indonesia,
    Honduras.id: Honduras,
    Ethiopia.id: Ethiopia,
    Chile.id: Chile,
    Brazil.id: Brazil,
    Bahrain.id: Bahrain,
    ThirdReich.id: ThirdReich,
    Yugoslavia.id: Yugoslavia,
    USSR.id: USSR,
    ItalianSocialRepublic.id: ItalianSocialRepublic,
}


def get_by_id(_id: int):
    """Returns a new country object for the given country id

    Args:
        _id: id for the country

    Returns:
        Country: a new country object
    """
    return country_dict[_id]()

