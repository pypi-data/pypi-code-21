class ParserException(Exception):
    def __init__(self, *args, **kwargs):
        self.details = kwargs.pop('details', None)
        self.redirect = kwargs.pop('redirect', None)
        self.status = kwargs.pop('status', None)
        super(Exception, self).__init__(*args, **kwargs)
