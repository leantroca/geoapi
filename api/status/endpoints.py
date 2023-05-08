from flask_restx import Namespace, Resource

from utils.geoserver_interface import Geoserver

geo = Geoserver()


namespace = Namespace(
    "Status", description=f"Endpoints for consulting status of {geo.hostname}."
)


@namespace.route("/layers")
class ListLayers(Resource):
    @namespace.doc("List Geoserver Layers.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    def get(self):
        return geo.list_layers()
