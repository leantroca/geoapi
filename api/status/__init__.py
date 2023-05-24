from flask_restx import Namespace

from utils.geoserver_interface import Geoserver


geoserver = Geoserver()

namespace = Namespace(
    "Status", description=f"Endpoints para consultar el estado del Geoserver ({geoserver.hostname}) {'&#9989;' if geoserver.status else '&#9940;'}."
)
