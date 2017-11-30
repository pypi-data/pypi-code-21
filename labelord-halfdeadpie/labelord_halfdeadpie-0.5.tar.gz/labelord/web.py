import flask
from flask import request
from flask import render_template
from .web_support import *
from .cli import cli
#####################################################################
# STARING NEW FLASK SKELETON (Task 2 - flask)
#check the config


class LabelordWeb(flask.Flask):
    """
    The class representing web part of the application

    has *my_session* - session for communication

    has *my_repos* - names of the user's repositories

    has *my_token* - user's GitHub token

    has *my_config* - name of the config file

    has *my_secret* - webhook secret

    has *last_label* - last processed label

    has *last_action* - last processed action

    """
    my_session = None
    my_repos = []
    my_token = None
    my_config = None
    my_secret = None
    last_label = ""
    last_action = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can do something here, but you don't have to...
        # Adding more args before *args is also possible
        # You need to pass import_name to super as first arg or
        # via keyword (e.g. import_name=__name__)
        # Be careful not to override something Flask-specific
        # @see http://flask.pocoo.org/docs/0.12/api/
        # @see https://github.com/pallets/flask
        import_name=__name__


    def inject_session(self, session):
        """
        Injects session

        :param session: requests session
        """
        # TODO: inject session for communication with GitHub
        # The tests will call this method to pass the testing session.
        # Always use session from this call (it will be called before
        # any HTTP request). If this method is not called, create new
        # session.
        self.my_session = session

    def reload_config(self):
        """
        Reload configuration file
        """
        # TODO: check envvar LABELORD_CONFIG and reload the config
        # Because there are problems with reimporting the app with
        # different configuration, this method will be called in
        # order to reload configuration file. Check if everything
        # is correctly set-up
        self.my_config = set_config()
        config = self.my_config
        self.my_repos = get_config_repos(config)
        self.my_token = get_tkn(config)
        self.my_secret = get_secret(config)

# TODO: instantiate LabelordWeb app
# Be careful with configs, this is module-wide variable,
# you want to be able to run CLI app as it was in task 1.
#app = flask.Flask(__name__)
#app = LabelordWeb(__name__)

def create_app():
    """
    Create application Labelord
    """
    app = LabelordWeb(__name__)
    app.my_config = set_config()
    return app

app=create_app()
# TODO: implement web app
# hint: you can use flask.current_app (inside app context)
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Process GET and POST methods
    """
    if(app.my_config == None):
        app.my_config = set_config()
    cfg = app.my_config
    repos = []
    repos = get_config_repos(cfg)
    app.my_token = get_tkn(cfg)
    app.my_secret = get_secret(cfg)

    r = request.method

    #GET METHOD
    if r == "GET":
        #return get_info(repos)
        return flask.render_template('index.html', repos=repos)

    #POST METHOD
    elif r == "POST":
        if check_signature(get_secret(cfg), request):
            if get_event(request) == "ping":
                return "ok"
            elif get_event(request) == "label":
                if(app.my_session == None):
                    app.my_session = requests.Session()
                app.my_session.headers = {'User-Agent': 'Python'}
                def token_auth(req):
                    req.headers['Authorization'] = 'token ' + app.my_token
                    return req
                app.my_session.auth = token_auth
                session = app.my_session

                repo = get_repo_name(request)
                if(repo in repos):
                    action = get_action(request)
                    name = get_lname(request)
                    color = get_lcolor(request)

                    if(name != app.last_label or action != app.last_action):
                        app.last_label = name
                        app.last_action = action
                        # CREATED
                        if (action == 'created'):
                            return create_label(name, color, repos, session, repo)
                        # EDITED
                        if (action == 'edited'):
                            old_name = get_old_name(request)
                            return edit_label(old_name, name, color, repos, session, repo)
                        # DELETED
                        if (action == 'deleted'):
                            return delete_label(name, repos, session, repo)
                    else:
                        return "OK"
                else:
                    code = 400
                    msg = 'BAD REQUEST'
                    return msg, code
        else:
            code = 401
            msg = 'UNAUTHORIZED'
            return msg, code

# Return info about application for GET method
def get_info(repos):
            """
            Returns info message about the application and repositories

            :param repos: The set of repositories
            """
            info = "labelord application is master-to-master application for label replication using webhook for GitHub<br>"
            for i in repos:
                info += i + ' ' + repo_link(i) + '<br>'
            return info

#return link to github and connected repo
@app.template_filter()
def repo_link(repo):
    """
    Returns the link to the repository

    :param repo: Name of the repository
    :return: Link to repository (String)
    """
    return "https://github.com/" + repo


@cli.command()
@click.pass_context
@click.option('--host', '-h', default="127.0.0.1")
@click.option('--port', '-p', default=5000)
@click.option('--debug', '-d', is_flag=True)
def run_server(ctx, host, port, debug):
    """Run server"""
    # TODO: implement the command for starting web app (use app.run)
    # Don't forget to app the session from context to app
    app.my_config = ctx.obj['config']
    app.my_session = ctx.obj['session']
    app.run(host,port,debug)
# ENDING  NEW FLASK SKELETON
#####################################################################