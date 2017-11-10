from sqlalchemy.orm.session import Session as SQLAlchemySession, make_transient


class Session(SQLAlchemySession):

    def __init__(self, engine, **kwargs):
        kwargs.setdefault('autocommit', False)
        super(Session, self).__init__(bind=engine, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO(dmu) LOW: Explore why self.expire_on_commit = False is need. The line was taken
        #                from previous solution
        self.expire_on_commit = False
        session_objects = list(self)

        commit_exception = None
        if exc_type:
            self.expunge_all()  # Remove all objects from session (must be called before rollback)
            self.rollback()
        else:
            try:
                self.commit()
            except Exception as ex:
                commit_exception = ex

        # Disconnect session objects for SQLAlchemy completely
        for obj in session_objects:
            make_transient(obj)

        self.close()

        if commit_exception:
            raise commit_exception  # re-raise exception
