# --
# Copyright (c) 2008-2017 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from sqlalchemy import Table, Column, Unicode
from sqlalchemy import MetaData

__metadata__ = MetaData()

# -----------------------------------------------------------------------------

page_data = Table(
    'page', __metadata__,
    Column('pagename', Unicode, primary_key=True),
    Column('data', Unicode(10 * 1024)),
    Column('creator', Unicode(40))
)
