from flask_restx import Namespace

namespace = Namespace(
    "Geoserver",
    description="Endpoints for managing layers in wms.minhabitat.gob.ar.",
)