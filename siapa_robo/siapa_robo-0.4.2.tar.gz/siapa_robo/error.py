class SIAPAerrorProcessor():
    pass


class SIAPAerror():
    self.code
    self.reason

    def __repr__(self):
        return f"Erro SIAPA {self.code} {self.reason}"
