class Datum:
    """ Třída zapouzdřující chování obecného datumu.. """

    def __init__(self, den, mesic, rok):
        self.den = den
        self.mesic = mesic
        self.rok = rok

    def ToString(self):
        rok = str(self.rok)
        mesic = str(self.mesic).zfill(2)
        den = str(self.den).zfill(2)
        return rok + "-" + mesic + "-" + den
