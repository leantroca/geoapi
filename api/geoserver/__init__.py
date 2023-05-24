from flask_restx import Namespace
from utils.geoserver_interface import Geoserver

geo = Geoserver()


namespace = Namespace(
    "Geoserver",
    description=f"Endpoints for managing layers in {geo.hostname}.",
)
