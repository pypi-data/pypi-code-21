# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Administration."""
from ..i18n import _
from ..update import versions, update

from .view import ViewBase, ViewPageTemplateFile


class Update(ViewBase):
  template = ViewPageTemplateFile("controlled_page.pt")

  def updatable(self):
    vs = versions()
    return vs[0] > vs[1]

  def __call__(self):
    update()
    return self.template(body=self.translate(_(u"Updated")))
