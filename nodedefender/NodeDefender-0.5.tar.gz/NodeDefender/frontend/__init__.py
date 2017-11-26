from NodeDefender import app, LoginMan, serializer
from flask_login import login_required, current_user
import NodeDefender
from itsdangerous import URLSafeSerializer

@LoginMan.user_loader
def load_user(id):
    return NodeDefender.db.sql.UserModel.query.get(id)

@app.context_processor
def inject_user():      # Adds general data to base-template
    if current_user:
        # Return Message- inbox for user if authenticated
        return dict(current_user = current_user)
    else:
        # If not authenticated user get Guest- ID(That cant be used).
        return dict(current_user = None)


@app.context_processor
def inject_serializer():
    def serialize(name):
        return serializer.dumps(name)
    def serialize_salted(name):
        return serializer.dumps_salted(name)
    return dict(serialize = serialize, serialize_salted = serialize_salted)

def trim_string(string):
    return string.replace(" ", "")

app.jinja_env.globals.update(trim=trim_string)

import NodeDefender.frontend.views
import NodeDefender.frontend.sockets
