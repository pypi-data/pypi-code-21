import random

class Mesic:
    """ Třída zapouzdřující chování měsíce.. """
    def __init__(self):
        self.mesice = ('leden', 'únor', 'březen', 'duben', 'květen', 'červen', 'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec')
        self.nazev = ""
        self.cislo = 0

    def SetMesic(self, cislo):
        self.cislo = cislo
        self.nazev = self.mesice[cislo-1]

    def SetRandom(self):
        i = random.randint(1, 12)
        self.SetMesic(i)

def GetRandomMesicNazev():
    """ Předej mi náhodný název měsíce.. """
    m = Mesic()
    m.SetRandom()
    return m.nazev

def GetRandomMesicCislo():
    """ Předej mi náhodné číslo měsíce.. """
    m = Mesic()
    m.SetRandom()
    return m.cislo
