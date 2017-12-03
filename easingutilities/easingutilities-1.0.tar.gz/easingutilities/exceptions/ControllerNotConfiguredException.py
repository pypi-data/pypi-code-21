from easingutilities.exceptions.EasingException import EasingException


class ControllerNotConfiguredException(EasingException):
    def __init__(self, message):
        self.message = message
