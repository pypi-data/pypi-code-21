from feincms.models import Base, Template as FeinCMSTemplate
from feincms.module.page.models import Page

class Template(FeinCMSTemplate):

    """Overload the FeinCMS template to add the 'children' option."""

    def __init__(self, *args, **kwargs):
        if 'children' in kwargs:
            self.children = kwargs['children']
            del(kwargs['children'])
        super(Template, self).__init__(*args, **kwargs)
