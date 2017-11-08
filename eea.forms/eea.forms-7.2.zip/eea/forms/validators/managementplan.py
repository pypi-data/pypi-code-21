""" Management plan validator
"""
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

class ManagementPlanCodeValidator(object):
    """ Validator
    """
    implements(IValidator)

    def __init__(self,
                 name,
                 title='Management plan code',
                 description='Management plan code validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        """ check if management plan code is in right format """
        # check we have 3 digits separated by dots
        errmsg = "Validation failed, management plan code is not in " \
                 "the format #.#.# e.g. 1.5.2"
        digits = value[1].split('.')
        if len(digits) == 3:
            for dig in digits:
                try:
                    int(dig)
                except ValueError:
                    return errmsg
            return 1
        return errmsg
