"""
Custom Exceptions used for testing for the Clinical Research Study Manager package
"""

class MyException(ValueError):
    def __init__(self, *args):
        super().__init__(*args)


class HeaderException(MyException):
    def __init__(self, *args):
        super().__init__(*args)


class InputException(MyException):
    """
    Exceptions for different user inputs. Will display a different error message based on the input type.
    If input type is not one of the given exceptions will default to the error message in the called functions.
    """

    def __init__(self, *args):
        super().__init__(*args)
