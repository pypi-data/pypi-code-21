# -*- coding: utf-8 -*-
"""add client delay

Revision ID: 76d52bb064b8
Revises: 7c7d205787b0
Create Date: 2017-02-07 14:46:11.268920

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '76d52bb064b8'
down_revision = u'7c7d205787b0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # client
    op.add_column('client', sa.Column('delay', sa.Integer(), nullable=True))


def downgrade():

    # client
    op.drop_column('client', 'delay')
