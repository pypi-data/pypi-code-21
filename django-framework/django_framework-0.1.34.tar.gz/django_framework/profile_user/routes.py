
from auth_token.routes import routes as auth_token_routes
from profile.routes import routes as profile_routes
from user.routes import routes as user_routes


routes = []

routes += auth_token_routes
routes += profile_routes
routes += user_routes
