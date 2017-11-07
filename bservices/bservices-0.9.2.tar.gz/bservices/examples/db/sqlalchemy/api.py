# coding: utf-8
import sys

from oslo_config import cfg
from oslo_db import options as oslo_db_options
from oslo_db.sqlalchemy import utils as sqlalchemyutils
from oslo_log import log as logging

from bservices.db.sqlalchemy import get_engine, get_session

from . import models

CONF = cfg.CONF
CONF.register_opts(oslo_db_options.database_opts, 'database')
oslo_db_options.set_defaults(CONF, connection="sqlite:///:memory:")
DB_INIT = False

LOG = logging.getLogger(__name__)


def get_backend():
    """The backend is this module itself."""
    global DB_INIT
    if not DB_INIT:
        models.TestData.metadata.create_all(get_engine(CONF.database))
        DB_INIT = True
    return sys.modules[__name__]


###########################################################
# API Interface
def get_data(_id):
    model = models.TestData
    session = get_session(CONF.database)
    query = sqlalchemyutils.model_query(model, session)
    obj = query.filter_by(id=_id).first()
    if obj:
        return {
            "id": obj.id,
            "data": obj.data
        }
    else:
        return None


def set_data(data):
    model = models.TestData
    session = get_session(CONF.database)
    obj = model(data=data)
    obj.save(session)
    return {
        "id": obj.id,
    }
