class StopValidation(Exception):
    pass


class BaseValidationError(Exception):
    def flatten(self):
        raise NotImplementedError


class SimpleValidationError(BaseValidationError):
    def __init__(self, code, path=None, extra=None):
        super().__init__()
        self.code = code
        self.path = path or []
        self.extra = extra

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'({self.code!r}, path={self.path!r}, extra={self.extra!r})'
        )

    def flatten(self):
        return [self]


class CompoundValidationError(BaseValidationError):
    def __init__(self, errors):
        super().__init__()
        self.errors = errors

    def __repr__(self):
        return f'{self.__class__.__name__}({self.errors!r})'

    def flatten(self):
        result = []
        for any_error in self.errors:
            for simple_error in any_error.flatten():
                result.append(simple_error)
        return result


class NestedValidationError(BaseValidationError):
    def __init__(self, key, error):
        super().__init__()
        self.key = key
        self.error = error

    def __repr__(self):
        return f'{self.__class__.__name__}({self.key!r}, {self.error!r})'

    def flatten(self):
        result = []
        for error in self.error.flatten():
            error_path = [self.key] + error.path
            result.append(
                SimpleValidationError(error.code, error_path, error.extra),
            )
        return result
