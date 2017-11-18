# This file is generated from pydcs_export.lua

from . import unittype


class Armed_speedboat(unittype.ShipType):
    id = "speedboat"
    name = "Armed speedboat"


class CVN_70_Carl_Vinson(unittype.ShipType):
    id = "VINSON"
    name = "CVN-70 Carl Vinson"
    plane_num = 72
    helicopter_num = 6
    parking = 4


class FFG_7CL_Oliver_Hazzard_Perry(unittype.ShipType):
    id = "PERRY"
    name = "FFG-7CL Oliver Hazzard Perry"
    helicopter_num = 2
    parking = 1


class CG_60_Normandy(unittype.ShipType):
    id = "TICONDEROG"
    name = "CG-60 Normandy"
    helicopter_num = 2
    parking = 1


class FFL_1124_4_Grisha(unittype.ShipType):
    id = "ALBATROS"
    name = "FFL 1124.4 Grisha"


class CV_1143_5_Admiral_Kuznetsov(unittype.ShipType):
    id = "KUZNECOW"
    name = "CV 1143.5 Admiral Kuznetsov"
    plane_num = 24
    helicopter_num = 12
    parking = 3


class FSG_1241_1MP_Molniya(unittype.ShipType):
    id = "MOLNIYA"
    name = "FSG 1241.1MP Molniya"


class CG_1164_Moskva(unittype.ShipType):
    id = "MOSCOW"
    name = "CG 1164 Moskva"
    helicopter_num = 1
    parking = 1


class FFG_11540_Neustrashimy(unittype.ShipType):
    id = "NEUSTRASH"
    name = "FFG 11540 Neustrashimy"
    helicopter_num = 1
    parking = 1


class CGN_1144_2_Pyotr_Velikiy(unittype.ShipType):
    id = "PIOTR"
    name = "CGN 1144.2 Pyotr Velikiy"
    helicopter_num = 1
    parking = 1


class FF_1135M_Rezky(unittype.ShipType):
    id = "REZKY"
    name = "FF 1135M Rezky"


class Tanker_Elnya_160(unittype.ShipType):
    id = "ELNYA"
    name = "Tanker Elnya 160"


class Dry_cargo_ship_Ivanov(unittype.ShipType):
    id = "Dry-cargo ship-2"
    name = "Dry cargo ship Ivanov"


class Bulk_cargo_ship_Yakushev(unittype.ShipType):
    id = "Dry-cargo ship-1"
    name = "Bulk cargo ship Yakushev"


class Civil_boat_Zvezdny(unittype.ShipType):
    id = "ZWEZDNY"
    name = "Civil boat Zvezdny"


class SSK_877(unittype.ShipType):
    id = "KILO"
    name = "SSK 877"


class SSK_641B(unittype.ShipType):
    id = "SOM"
    name = "SSK 641B"


class LST_Mk_II(unittype.ShipType):
    id = "LST_Mk2"
    name = "LST Mk.II"


class LS_Samuel_Chase(unittype.ShipType):
    id = "USS_Samuel_Chase"
    name = "LS Samuel Chase"

ship_map = {
    "speedboat": Armed_speedboat,
    "VINSON": CVN_70_Carl_Vinson,
    "PERRY": FFG_7CL_Oliver_Hazzard_Perry,
    "TICONDEROG": CG_60_Normandy,
    "ALBATROS": FFL_1124_4_Grisha,
    "KUZNECOW": CV_1143_5_Admiral_Kuznetsov,
    "MOLNIYA": FSG_1241_1MP_Molniya,
    "MOSCOW": CG_1164_Moskva,
    "NEUSTRASH": FFG_11540_Neustrashimy,
    "PIOTR": CGN_1144_2_Pyotr_Velikiy,
    "REZKY": FF_1135M_Rezky,
    "ELNYA": Tanker_Elnya_160,
    "Dry-cargo ship-2": Dry_cargo_ship_Ivanov,
    "Dry-cargo ship-1": Bulk_cargo_ship_Yakushev,
    "ZWEZDNY": Civil_boat_Zvezdny,
    "KILO": SSK_877,
    "SOM": SSK_641B,
    "LST_Mk2": LST_Mk_II,
    "USS_Samuel_Chase": LS_Samuel_Chase,
}
