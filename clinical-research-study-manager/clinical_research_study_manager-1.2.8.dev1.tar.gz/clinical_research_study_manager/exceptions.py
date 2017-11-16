"""
Custom exceptions for Clinical Research Study Manager package
"""

class MyException(ValueError):
    def __init__(self, msg):
        super().__init__(msg)


class HeaderException(MyException):
    def __init__(self, msg):
        super().__init__(msg)


class InputException(MyException):
    """
    Exceptions for different user inputs. Will display a different error message based on the input type.
    If input type is not one of the given exceptions will default to the error message in the called functions.
    """

    def __init__(self, msg, input_type):
        messages = dict()
        messages['age'] = 'Please enter a number greater than 0'
        messages['enrollment status'] = 'Please enter Y, N, NA'
        messages['eligibility status'] = 'Please enter Y, N, NA'
        messages['follow up complete'] = 'Please enter Y, N, NA'
        messages['sex'] = 'Please enter M, F, O, U'
        if messages.get(input_type) is not None:
            msg = messages[input_type]
        else:
            msg = msg
        super().__init__(msg)
