import random

from pyranda.okres import Okres

class Kraj:
    """Objekt pro zapouzdření informací o kraji jako územním celku.."""
    def __init__(self, nazev, oznaceni, mesto):
        self.nazev = nazev
        self.oznaceni = oznaceni
        self.mesto = mesto
        self.okress = []

    def addOkres(self, okres):
        """ Každý kraj může obsahovat jeden anebo více okresů.. """
        self.okress.append(okres)

    def hasOkres(self, okres):
        """ Je námi definovaný okres součístí tohoto kraje? """
        for item in self.okress:
            if item.IsEqual(okres):
                return True
        return False
