from trunity_migrator.fixers import *


class HTMLFixer(object):

    def __init__(self, settings):
        self._settings = settings
        self._fixers = settings.FIXERS_ALLOWED

    def apply(self, html: str):
        """
        Apply fixers listed in settings to html content.

        :param html:
        :return:
        """
        for fixer in self._fixers:
            fixer_kwargs = getattr(
                self._settings,
                fixer.upper()
            )
            html = eval(fixer)(html, **fixer_kwargs)
        return html
