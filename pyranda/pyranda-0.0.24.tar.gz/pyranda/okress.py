import random

from pyranda.okres import Okres

class Okress:
    def __init__(self):
        # Veřejné pole s okresy..
        self.okres = []

        # Středočeský kraj
        self.okres.append(Okres("Benešov", "BN", "Benešov"))
        self.okres.append(Okres("Beroun", "BE", "Beroun"))
        self.okres.append(Okres("Kladno", "KD", "Kladno"))
        self.okres.append(Okres("Kolín", "KO", "Kolín"))
        self.okres.append(Okres("Kutná Hora", "KH", "Kutnái Hora"))
        self.okres.append(Okres("Mělník", "ME", "Mělník"))
        self.okres.append(Okres("Mladá Boleslav", "MB", "Mladá Boleslav"))
        self.okres.append(Okres("Nymburk", "NB", "Nymburk"))
        self.okres.append(Okres("Praha-východ", "PY", "Praha-východ"))
        self.okres.append(Okres("Praha-západ", "PZ", "Praha-západ"))
        self.okres.append(Okres("Příbram", "PB", "Příbram"))
        self.okres.append(Okres("Rakovník", "RA", "Rakovník"))

        # Jihočeský kraj
        self.okres.append(Okres("České Budějovice", "CB", "České Budějovice"))
        self.okres.append(Okres("Český Krumlov", "CK", "Český Krumlov"))
        self.okres.append(Okres("Jindřichův Hradec", "JH", "Jindřichův Hradec"))
        self.okres.append(Okres("Písek", "OI", "Písek"))
        self.okres.append(Okres("Prachatice", "PT", "Prachatice"))
        self.okres.append(Okres("Strakonice", "ST", "Strakonice"))
        self.okres.append(Okres("Tábor", "TA", "Tábor"))

        # Plzeňský kraj
        self.okres.append(Okres("Domažlice", "DO", "Domažlice"))
        self.okres.append(Okres("Klatovy", "KT", "Klatovy"))
        self.okres.append(Okres("Plzeň-jih", "PJ", "Plzeň-jih"))
        self.okres.append(Okres("Plzeň-město", "PM", "Plzeň-město"))
        self.okres.append(Okres("Plzeň-sever", "PS", "Plzeň-sever"))
        self.okres.append(Okres("Rokycany", "RO", "Rokycany"))
        self.okres.append(Okres("Tachov", "TC", "Tachov"))

        # Karlovarský kraj
        self.okres.append(Okres("Cheb", "CH", "Cheb"))
        self.okres.append(Okres("Karlovy Vary", "KV", "Karlovy Vary"))
        self.okres.append(Okres("Sokolov", "SO", "Sokolov"))

       # Ústecký kraj
        self.okres.append(Okres("Děčín", "DC", "Děčín"))
        self.okres.append(Okres("Chomutov", "CV", "Chomutov"))
        self.okres.append(Okres("Litoměřice", "LT", "Litoměřice"))
        self.okres.append(Okres("Louny", "LN", "Louny"))
        self.okres.append(Okres("Most", "MO", "Most"))
        self.okres.append(Okres("Teplice", "TP", "Teplice"))
        self.okres.append(Okres("Ústí nad Labem", "UL", "Ústí nad Labem"))

        # Liberecký kraj
        self.okres.append(Okres("Česká Lípa", "CL", "Česká Lípa"))
        self.okres.append(Okres("Jablonec nad Nisou", "JN", "Jablonec nad Nisou"))
        self.okres.append(Okres("Liberec", "LI", "Liberec"))
        self.okres.append(Okres("Semily", "SM", "Semily"))

        # Královéhradecký kraj
        self.okres.append(Okres("Hradec Králové", "HK", "Hradec Králové"))
        self.okres.append(Okres("Jičín", "JC", "Jičín"))
        self.okres.append(Okres("Náchod", "NA", "Náchod"))
        self.okres.append(Okres("Rychnov nad Kněžnou", "RK", "Rychnov nad Kněžnou"))
        self.okres.append(Okres("Trutnov", "TU", "Trutnov"))

        # Pardubický kraj
        self.okres.append(Okres("Chrudim", "CR", "Chrudim"))
        self.okres.append(Okres("Pardubice", "PU", "Pardubice"))
        self.okres.append(Okres("Svitavy", "SY", "Svitavy"))
        self.okres.append(Okres("Ústí nad Orlicí", "UO", "Ústí nad Orlicí"))

        # Kraj Vysočina
        self.okres.append(Okres("Havlíčkův Brod", "HB", "Havlíčkův Brod"))
        self.okres.append(Okres("Jihlava", "JI", "Jihlava"))
        self.okres.append(Okres("Pelhřimov", "PE", "Pelhřimov"))
        self.okres.append(Okres("Třebíč", "TR", "Třebíč"))
        self.okres.append(Okres("Žďár nad Sázavou", "ZR", "Žďár nad Sázavou"))

        # Jihomoravský kraj
        self.okres.append(Okres("Blansko", "BK", "Blansko"))
        self.okres.append(Okres("Brno-město", "BM", "Brno-město"))
        self.okres.append(Okres("Brno-venkov", "BI", "Brno-venkov"))
        self.okres.append(Okres("Břeclav", "BV", "Břeclav"))
        self.okres.append(Okres("Hodonín", "HO", "Hodonín"))
        self.okres.append(Okres("Vyškov", "VY", "Vyškov"))
        self.okres.append(Okres("Znojmo", "ZN", "Znojmo"))

        # Olomoucký kraj
        self.okres.append(Okres("Jeseník", "JE", "Jeseník"))
        self.okres.append(Okres("Olomouc", "OC", "Olomouc"))
        self.okres.append(Okres("Prostějov", "PV", "Prostějov"))
        self.okres.append(Okres("Přerov", "PR", "Přerov"))
        self.okres.append(Okres("Šumperk", "SU", "Šumperk"))
 
        # Moravskoslezský kraj
        self.okres.append(Okres("Bruntál", "BR", "Bruntál"))
        self.okres.append(Okres("Frýdek-Místek", "FM", "Frýdek-Místek"))
        self.okres.append(Okres("Karviná", "KI", "Karviná"))
        self.okres.append(Okres("Nový Jičín", "NJ", "Nový Jičín"))
        self.okres.append(Okres("Opava", "OP", "Opava"))
        self.okres.append(Okres("Ostrava-město", "OV", "Ostrava-město"))

        # Zlínský kraj
        self.okres.append(Okres("Kroměříž", "KM", "Kroměříž"))
        self.okres.append(Okres("Uherské Hradiště", "UH", "Uherské Hradiště"))
        self.okres.append(Okres("Vsetín", "VS", "Vsetín"))
        self.okres.append(Okres("Zlín", "ZL", "Zlín"))
