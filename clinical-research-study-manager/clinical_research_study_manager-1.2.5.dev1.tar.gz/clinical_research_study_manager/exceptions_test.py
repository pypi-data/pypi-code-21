# TODO: Add custom exceptions for each input type i.e. make sure age isn't a negative number
# TODO: Also figure out how to map an exception to the input type. Do that in the class definition?


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
