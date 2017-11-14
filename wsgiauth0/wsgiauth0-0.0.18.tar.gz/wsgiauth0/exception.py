"""Exception class for wsgiauth0."""


class Error(Exception):

    def __init__(self, code, description):
        super(Exception, self).__init__(code, description)

    def __repr__(self):
        return '<%s code="%s">' % (self.__class__, self.args[0])

    def to_dict(self):
        return {
            'code': self.args[0],
            'description': self.args[1],
            'origin': self,
        }
