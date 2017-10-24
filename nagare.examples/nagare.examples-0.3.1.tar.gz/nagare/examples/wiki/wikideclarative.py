# --
# Copyright (c) 2008-2017 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from sqlalchemy import Column, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

__metadata__ = MetaData()

# -----------------------------------------------------------------------------

Base = declarative_base(metadata=__metadata__)


class PageData(Base):
    __tablename__ = 'page'

    # id = Column(Integer, primary_key=True)
    pagename = Column(Unicode, primary_key=True)
    data = Column(Unicode(10 * 1024))
    creator = Column(Unicode(40))

    def __init__(self, pagename, data, creator):
        self.pagename = pagename
        self.data = data
        self.creator = creator

# -----------------------------------------------------------------------------


def populate():
    page = PageData(u'FrontPage', u'Welcome to my *WikiWiki* !', u'admin')
    # database.session.add(page)

    page = PageData(
        u'WikiWiki', u'On this *WikiWiki*, the page contents can be '
        'written in `Restructured Text <http://docutils.sourceforge.net/rst.html>`_',
        u'john'
    )
    # database.session.add(page)
