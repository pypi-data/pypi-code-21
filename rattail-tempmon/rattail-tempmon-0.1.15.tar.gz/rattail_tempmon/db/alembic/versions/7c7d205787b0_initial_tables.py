# -*- coding: utf-8 -*-
"""initial tables

Revision ID: 7c7d205787b0
Revises: 
Create Date: 2016-12-05 15:14:09.387668

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '7c7d205787b0'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # client
    op.create_table('client',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('config_key', sa.String(length=50), nullable=False),
                    sa.Column('hostname', sa.String(length=255), nullable=False),
                    sa.Column('location', sa.String(length=255), nullable=True),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('online', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('config_key', name=u'client_uq_config_key')
    )

    # probe
    op.create_table('probe',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('client_uuid', sa.String(length=32), nullable=False),
                    sa.Column('config_key', sa.String(length=50), nullable=False),
                    sa.Column('appliance_type', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=False),
                    sa.Column('device_path', sa.String(length=255), nullable=True),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('good_temp_min', sa.Integer(), nullable=False),
                    sa.Column('good_temp_max', sa.Integer(), nullable=False),
                    sa.Column('critical_temp_min', sa.Integer(), nullable=False),
                    sa.Column('critical_temp_max', sa.Integer(), nullable=False),
                    sa.Column('therm_status_timeout', sa.Integer(), nullable=False),
                    sa.Column('status_alert_timeout', sa.Integer(), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.Column('status_changed', sa.DateTime(), nullable=True),
                    sa.Column('status_alert_sent', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['client_uuid'], [u'client.uuid'], name=u'probe_fk_client'),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('config_key', name=u'probe_uq_config_key')
    )

    # tempmon reading
    op.create_table('reading',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('client_uuid', sa.String(length=32), nullable=False),
                    sa.Column('probe_uuid', sa.String(length=32), nullable=False),
                    sa.Column('taken', sa.DateTime(), nullable=False),
                    sa.Column('degrees_f', sa.Numeric(precision=7, scale=4), nullable=False),
                    sa.ForeignKeyConstraint(['client_uuid'], [u'client.uuid'], name=u'reading_fk_client'),
                    sa.ForeignKeyConstraint(['probe_uuid'], [u'probe.uuid'], name=u'reading_fk_probe'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():
    op.drop_table('reading')
    op.drop_table('probe')
    op.drop_table('client')
