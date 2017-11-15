import flask
import sepiida.session

def extract_credentials(_request):
    if flask.has_request_context():
        user     = sepiida.session.current_user_uri()
        username = _request.authorization['username'] if _request.authorization else None
        password = _request.authorization['password'] if _request.authorization else None
        session  =  _request.cookies.get('session', None)
    else:
        user     = None
        username = None
        password = None
        session  = None
    return {
        'password'  : password,
        'session'   : session,
        'user'      : user,
        'username'  : username,
    }
