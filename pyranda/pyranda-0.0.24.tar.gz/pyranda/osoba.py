class Osoba:
    """Objekt pro zapouzdření informací o osobě.."""
    def __init__(self, nazev, jmeno, prijmeni, dnar):
        self.nazev = nazev
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.dnar = dnar
        self.email = ""
        

    def IsEqual(self, osoba):
        """ Porovnáme dva osoby a pokud jsou schodné vracíme True.. """
        if self.nazev == osoba.nazev and self.prijmeni == osoba.prijmeni and self.dnar == osoba.dnar:
            return True
        return False


    def AddEmail(self, email):
        self.email = email
