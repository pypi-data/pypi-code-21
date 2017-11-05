import getpass

class Input():
    def __init__(self, identifier):
        self.identifier = identifier
    def get_identifier(self):
        return self.identifier
    def retrieve(self):
        return input(self.identifier + ": ")

class IntegerInput(Input):
    def retrieve(self):
        return int(super().retrieve())

class FloatInput(Input):
    def retrieve(self):
        return float(super().retrieve())

class ListInput(Input):
    def __init__(self, identifier, separator = ','):
        super().__init__(identifier)
        self.separator = separator
    def retrieve(self):
        return super().retrieve().split(self.separator)

class MaskedInput(Input):
    def retrieve(self):
        return getpass.getpass(self.identifier + ": ")

class Form():
    def __init__(self):
        self.inputs = []
        self.results = []
    def add_input(self, input):
        self.inputs.append(input)
        return self
    def run(self):
        result = []
        for input in self.inputs:
            result.append((input.get_identifier(), input.retrieve()))
        self.results.append(result)
        return self
    def get_results(self):
        return self.results