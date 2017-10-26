from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)


class SQLAlchemySessionMiddleware:
    def __init__(self, engine):
        session_factory = sessionmaker(bind=engine)
        self.mksession = scoped_session(session_factory)

    def process_resource(self, req, resp, resource, params):
        resource.session = self.mksession()

    def process_response(self, req, resp, resource, req_succeeded):
        if not hasattr(resource, 'session'):
            return

        if not req_succeeded:
            resource.session.rollback()
        else:
            resource.session.commit()
            resource.session.close()
