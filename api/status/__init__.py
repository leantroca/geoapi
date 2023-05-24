from flask_restx import Namespace

from utils.geoserver_interface import Geoserver


geoserver = Geoserver()

namespace = Namespace(
    "Status", description=f"Endpoints para consultar el estado de {geoserver.hostname}."
)
