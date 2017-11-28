
from model_api.routes import routes as model_api_routes
from model_jobs_api.routes import routes as model_jobs_api_routes

routes = []
routes += model_api_routes
routes += model_jobs_api_routes
