import random

class RodneCislo:
    """ Třída zapouzdřující chování rodného čísla.. """

    def __init__(self):
        self.cislo = ""
        self.rok = 0
        self.mesic = 0
        self.den = 0
        self.pohlavi = 0


    def SetCislo(self, cislo):
        """ Načtení atributů rodného číslo z předaného rodného čísla.. """
        if cislo == "" or cislo == "000000/0000":
            self.cislo = ""
            self.rok = 0
            self.mesic = 0
            self.den = 0
            self.pohlavi = 0
            return

        self.set_cislo(cislo)
        self.set_rok()
        self.set_mesic()
        self.set_den()
        self.set_pohlavi()


    def SetRandom(self):
        """ Vytvoření náhodného rodného čísla.. """
        rok = random.randint(1900, 2054)
        mesic = random.randint(1, 12)
        den = random.randint(1, 31)
        pohlavi = random.randint(1, 2)
        poradi = random.randint(1,9999)

        self.Build(rok, mesic, den, pohlavi, poradi)


    def Build(self, rok, mesic, den, pohlavi, poradi):
        """ Sestavení rodného čísla podle parametrů.. """
        if pohlavi == 2:
                mesic += 50

        self.rok = rok
        self.mesic = mesic
        self.den = den
        self.pohlavi = pohlavi
        self.poradi = poradi

        self.cislo = str(rok)[2:] + str(mesic).zfill(2) + str(den).zfill(2) + "/" + str(poradi)


    def set_cislo(self, cislo):
        """ Nastavení rodného čísla.. """
        self.cislo = cislo

    def set_rok(self):
        """ Nastavení roku narození z rodného čísla.. """
        rok = int(self.cislo[:2])
        if len(self.cislo) == 10:
            rok += 1900
        if len(self.cislo) == 11 and rok >= 54:
            rok += 1900
        if len(self.cislo) == 11 and rok < 54:
            rok += 2000

        self.rok = rok

    def set_mesic(self):
        """ Nastavení měsíce narození z rodného čísla.. """
        mesic = int(self.cislo[2:4])
        if mesic > 70:
            mesic -= 70
        if mesic > 50:
            mesic -= 50
        if mesic > 20:
            mesic -= 20
        self.mesic = mesic

    def set_den(self):
        """ Nastavení čísla dne narození.. """
        self.den = int(self.cislo[4:6])

    def set_pohlavi(self):
        """ Nastavení pohlaví podle rodného čísla.. """
        pohlavi = 1
        mesic = int(self.cislo[2:4])
        if mesic > 50:
            pohlavi = 2
        self.pohlavi = pohlavi
