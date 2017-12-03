from easingutilities.exceptions.EasingException import EasingException


class EasingNotConfiguredException(EasingException):
    def __init__(self, message):
        self.message = message
