import random

from pyranda.kraj import Kraj
from pyranda.okres import Okres

class Krajs:
    """ Objekt obsahující jednotlivé kraje v ČR.. """
    def __init__(self):
        self.kraj = []
        self.kraj.append(Kraj("Hlavní město Praha", "PHA", "Praha"))
        self.kraj.append(Kraj("Středočeský kraj",  "STČ", "Praha"))
        self.kraj.append(Kraj("Jihočeský kraj", "KJČ", "České Budějovice"))
        self.kraj.append(Kraj("Plzeňský kraj",  "KPL", "Plzeň"))
        self.kraj.append(Kraj("Karlovarský kraj", "KVK", "Karlovy Vary"))
        self.kraj.append(Kraj("Ústecký kraj", "KUL", "Ústí nad Labem"))
        self.kraj.append(Kraj("Liberecký kraj",  "KLB", "Liberec"))
        self.kraj.append(Kraj("Královéhradecký kraj", "KHK", "Hradec Králové"))
        self.kraj.append(Kraj("Pardubický kraj", "KPA", "Pardubice"))
        self.kraj.append(Kraj("Olomoucký kraj", "KOL", "Olomouc"))
        self.kraj.append(Kraj("Moravskoslezský kraj", "MSK", "Ostrava"))
        self.kraj.append(Kraj("Jihomoravský kraj", "JMK", "Brno"))
        self.kraj.append(Kraj("Zlínský kraj", "ZLK", "Zlín"))
        self.kraj.append(Kraj("Kraj Vysočina", "VYS", "Jihlava"))

    def getNazev(self, oznaceni):
        """ Předání názvu krajs z jeho označení.. """
        for item in self.kraj:
            if item.oznaceni == oznaceni:
                return item.nazev
        return "N/A"

    def getMesto(self, oznaceni):
        """ Předání názvu krajského města podle označení krajs.. """
        for item in self.kraj:
            if item.oznaceni == oznaceni:
                return item.mesto
        return "N/A"


def getRandomKraj():
    """ Předá náhodný kraj jako objekt.. """
    krajs = Krajs()
    index = random.randint(0, len(krajs.kraj)-1)
    return krajs.kraj[index]


def list_kraj():
    """ Zobrazení všech krajů.. """
    print()
    print("Výpsání všech krajů")
    print("-------------------")
    krajs = Krajs()
    for kraj in krajs.kraj:
        print(kraj.nazev)

    print()
    print("Výpsání náhodných krajů")
    print("-----------------------")
    for i in range(0,20):
        kraj = getRandomKraj()
        print(kraj.nazev + ", " + kraj.oznaceni + ", " + kraj.mesto)
