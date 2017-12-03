from easingutilities.exceptions.EasingException import EasingException


class WrongMovementException(EasingException):
    def __init__(self, message):
        self.message = message
