from flask_restx import Namespace, Resource

from utils.geoserver_interface import Geoserver

from .core import get_log_record

geo = Geoserver()


namespace = Namespace(
    "Status", description=f"Endpoints for consulting status of {geo.hostname}."
)


@namespace.route("/layers")
class ListLayers(Resource):
    @namespace.doc("List Geoserver Layers.")
    def get(self):
        return geo.list_layers()


@namespace.route("/batch/<int:id>")
class ProcessStatus(Resource):
    @namespace.doc("Process status.")
    def get(self, id):
        return get_log_record(id=id)
