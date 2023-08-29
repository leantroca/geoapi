from flask import Blueprint
from flask_restx import Api

from .geoserver.endpoints import namespace as geoserver
from .status.endpoints import namespace as status
from .styles.endpoints import namespace as styles

blueprint = Blueprint("api", __name__)
api = Api(blueprint)

api.add_namespace(status, path="/status")
api.add_namespace(geoserver, path="/geoserver")
api.add_namespace(styles, path="/styles")
