from flask import Blueprint
from flask_restx import Api

from .geoserver.endpoints import namespace as geoserver_ns
from .postgis.endpoints import namespace as postgis_ns
from .status.endpoints import namespace as status_ns
from .styles.endpoints import namespace as styles_ns

blueprint = Blueprint("api", __name__)
api = Api(blueprint)

api.add_namespace(status_ns, path="/status")
api.add_namespace(geoserver_ns, path="/geoserver")
api.add_namespace(styles_ns, path="/styles")
api.add_namespace(postgis_ns, path="/postgis")
