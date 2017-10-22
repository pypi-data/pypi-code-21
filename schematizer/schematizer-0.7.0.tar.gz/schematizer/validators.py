from schematizer.exceptions import SimpleValidationError, StopValidation


class BaseValidator:
    def validate_primitive(self, obj):
        pass

    def validate_native(self, obj):
        pass


class NullableValidator(BaseValidator):
    def validate(self, obj):
        if obj is None:
            raise StopValidation()

    def validate_primitive(self, obj):
        self.validate(obj)

    def validate_native(self, obj):
        self.validate(obj)


class LengthValidator(BaseValidator):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def validate_native(self, obj):
        length = len(obj)
        if self.min is not None and length < self.min:
            code = 'TOO_SHORT'
        elif self.max is not None and length > self.max:
            code = 'TOO_LONG'
        else:
            code = None
        if code:
            raise SimpleValidationError(code, extra={
                'min': self.min,
                'max': self.max,
            })


class RangeValidator(BaseValidator):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def validate_native(self, obj):
        if self.min is not None and obj < self.min:
            code = 'TOO_SMALL'
        elif self.max is not None and obj > self.max:
            code = 'TOO_BIG'
        else:
            code = None
        if code:
            raise SimpleValidationError(code, extra={
                'min': self.min,
                'max': self.max,
            })


Nullable = NullableValidator
Length = LengthValidator
Range = RangeValidator
