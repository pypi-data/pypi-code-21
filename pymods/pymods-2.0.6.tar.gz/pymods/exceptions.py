class PymodsException(Exception):
    def __str__(self):
        pass


class NameSpaceInvalid(PymodsException):
    def __str__(self):
        return "Root is in an unexpected namespace"


class ElementNotFound(PymodsException):
    def __str__(self):
        return "Record does not contain the specified element"


class ComplexElement(PymodsException):
    def __str__(self):
        return "Complex Element. Requires a specialized function"
