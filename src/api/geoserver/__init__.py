from flask_restx import Namespace

from utils.geoserver_interface import Geoserver

geoserver = Geoserver()


namespace = Namespace(
    "Geoserver",
    description=f"Endpoints para administrar capas en Geoserver ({geoserver.hostname}) "
    f"{'&#9989;' if geoserver.status else '&#9940;'}.",
)
