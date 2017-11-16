class NonePathError(TypeError):
    def __init__(self):
        super(__class__, self).__init__("Path can not be None type.")


class NotUrlPathError(ValueError):
    def __init__(self, path):
        super(__class__, self).__init__(
            "Expected an url quoted path, got {}.".format(path))


class IsUrlPathError(ValueError):
    def __init__(self, path):
        super(__class__, self).__init__(
            "Expected an not url quoted path, got {}.".format(path)
        )


class ConflictUrlSpecError(ValueError):
    def __init__(self, us1, us2):
        super(__class__, self).__init__(
            "Conflict UrlSpecs: {0} and {1}".format(us1, us2))


class NotValidPathError(ValueError):
    def __init__(self, path):
        super(__class__, self).__init__(
            "Got an invalid path: {}.".format(path)
        )


class DirectoryNotFoundError(ValueError):
    def __init__(self, path):
        super(__class__, self).__init__(
            "Directory {0} not found.".format(path))


def http_error(e):
    def emsg(text):
        return {'status': 'ERROR', 'message': text}
    if isinstance(e, FileNotFoundError):
        return emsg("File {} not found.".format(e)), 404
    elif isinstance(e, DirectoryNotFoundError):
        return emsg("Directory {} not found.".format(e)), 404
    elif isinstance(e, NotADirectoryError):
        return emsg("{} is not a directory.".format(e)), 409
    elif isinstance(e, NonePathError):
        return emsg('Path can not be None.'), 400
    elif isinstance(e, FileExistsError):
        return emsg('File {} exists.'.format(e)), 409
    else:
        return emsg('Unknown error: {}'.format(e)), 500
