from flask import request
from flask_restx import Api, Namespace, Resource

from .marshal import import_kml_parser

namespace = Namespace(
    "Geoserver", description="Endpoints for managing layers in wms.minhabitat.gob.ar."
)


@namespace.route("/kml/import")
class ImportKML(Resource):
    @namespace.doc("KML File import.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    @namespace.expect(import_kml_parser, validate=True)
    def post(self):
        form = import_kml_parser.parse_args(trim=True, bundle_errors=True)
        return {
            "endpoint": "POST geoserver/import/kml",
            "form": f"{form}",
            "request": f"{request.__dict__}",
        }


@namespace.route("/kml/append")
class UpdateKML(Resource):
    @namespace.doc("KML File append.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    @namespace.expect(import_kml_parser, validate=True)
    def put(self):
        form = import_kml_parser.parse_args(trim=True, bundle_errors=True)
        return {
            "endpoint": "POST geoserver/append/kml",
            "form": f"{form}",
            "request": f"{request.__dict__}",
        }


@namespace.route("/kml/remove")
class DeleteKML(Resource):
    @namespace.doc("KML File removal.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    @namespace.expect(import_kml_parser, validate=True)
    def delete(self):
        form = import_kml_parser.parse_args(trim=True, bundle_errors=True)
        return {
            "endpoint": "POST geoserver/remove/kml",
            "form": f"{form}",
            "request": f"{request.__dict__}",
        }
