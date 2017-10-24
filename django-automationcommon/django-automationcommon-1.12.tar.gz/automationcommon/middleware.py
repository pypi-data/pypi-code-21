from automationcommon.models import clear_local_user, set_local_user


class RequestUserMiddleware(object):
    """
    Middleware that simply set's the request.user to be used for the audit trail.
    """
    @classmethod
    def process_request(cls, request):
        set_local_user(request.user)

    @classmethod
    def process_response(cls, request, response):
        """
        Clear the user to minimise the chance of a user being wrongly assigned.
        """
        clear_local_user()
        return response

    @classmethod
    def process_exception(cls, request, exception):
        """
        Clear the user to minimise the chance of a user being wrongly assigned.
        """
        clear_local_user()
