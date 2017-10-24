from .render_service import RenderService
from .project_service import ProjectService

import warnings

try:
	from . import Movie_pb2 as SDL
except Exception:
	warnings.warn("Cannot import 'Movie_pb2', movies will be blobs.")
	proto = None
