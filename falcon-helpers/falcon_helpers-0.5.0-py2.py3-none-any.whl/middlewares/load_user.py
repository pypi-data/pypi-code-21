import sqlalchemy as sa


class LoadUserMiddleware:
    """Load a user from the database during the request cycle using sqlalchemy

    By default this will grab the id data from the auth token on the request
    context assuming you are using `.middleware.auth_required`. To change that
    pass a function which takes the request and returns the user id to `get_id`.

    :param session: a sqlalchemy session
    :param user_cls: a class which will return the user object. This object must
        have a `get_by_id` which will return a SQLAlchemy Query.
    :param get_id: a function which will get the user identifier off of the
        request.

    """

    def __init__(self, session, user_cls, get_id=None):
        self.session = session
        self.user_cls = user_cls
        self.get_id = self._get_id

    @staticmethod
    def _get_id(req):
        try:
            return req.context.get('auth_token_contents').get('sub')
        except AttributeError as e:
            return None

    def fetch_user(self, user_id):
        return (self.user_cls
                    .get_by_id(user_id)
                    .with_session(self.session())
                    .one_or_none())

    def process_request(self, req, resp):
        user_id = self.get_id(req)
        req.context['user'] = self.fetch_user(user_id)
