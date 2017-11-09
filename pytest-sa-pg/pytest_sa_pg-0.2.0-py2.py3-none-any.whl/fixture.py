import pytest
from sqlalchemy import create_engine

from pytest_sa_pg import db


def engine_fixture(metadata, pgdatadir, port, initializer=None):

    @pytest.fixture(scope='session')
    def engine(request):
        db.setup_local_pg_cluster(request, pgdatadir, port)
        uri = 'postgresql://localhost:{}/postgres'.format(port)
        engine = create_engine(uri)
        if initializer is None:
            metadata.drop_all(engine)
            metadata.create_all(engine)
        else:
            initializer(engine, metadata)
        return create_engine(uri)

    return engine
