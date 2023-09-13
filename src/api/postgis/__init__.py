from flask_restx import Namespace

from utils.postgis_interface import PostGIS

postgis = PostGIS()


namespace = Namespace(
    "Postgis",
    description=f"Endpoints para administrar geometrías en Postgis ({postgis.host}) "
    f"{'&#9989;' if postgis.status else '&#9940;'}.",
)
