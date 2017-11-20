# -*- coding: utf-8; -*-
"""grow degrees

Revision ID: 75c09e11543c
Revises: 76d52bb064b8
Create Date: 2017-08-05 12:50:50.093173

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '75c09e11543c'
down_revision = u'76d52bb064b8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # reading
    op.alter_column('reading', 'degrees_f', type_=sa.Numeric(precision=8, scale=4))


def downgrade():

    # reading
    op.alter_column('reading', 'degrees_f', type_=sa.Numeric(precision=7, scale=4))
