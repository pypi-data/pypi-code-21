class Okres:
    """Objekt pro zapouzdření informací o okrese jako územním celku.."""
    def __init__(self, nazev, oznaceni, mesto):
        self.nazev = nazev
        self.oznaceni = oznaceni
        self.mesto = mesto

    def IsEqual(self, okres):
        """ Porovnáme dva okresy a pokud jsou schodné vracíme True.. """
        if self.nazev == okres.nazev and self.oznaceni == okres.oznaceni and self.mesto == okres.mesto:
            return True
        return False
