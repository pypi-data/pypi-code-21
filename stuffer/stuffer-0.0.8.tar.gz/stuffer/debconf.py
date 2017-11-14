from stuffer import apt
from stuffer.core import Action


class SetSelections(Action):
    """Specify debian configuration selections.

    The arguments will be passed to debconf-set-selections. See the
    `man page <http://manpages.ubuntu.com/manpages/xenial/man1/debconf-set-selections.1.html>`_ for details.

    Parameters
    ----------
    section
      Debconf section
    template
      Debconf template
    type_
      Debconf data type, e.g. ``select``, ``seen``.
    value
      Selection value
    """

    def __init__(self, section, template, type_, value):
        self.section = section
        self.template = template
        self.type_ = type_
        self.value = value
        super(SetSelections, self).__init__()

    def prerequisites(self):
        return [apt.Install('debconf-utils', update=False)]

    def command(self):
        return "echo {} {} {} {} | debconf-set-selections".format(self.section, self.template, self.type_, self.value)
