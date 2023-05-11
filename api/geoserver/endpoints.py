from flask import request
from flask_restx import Namespace, Resource
import json

from . import namespace
from .core import load_post_kml, ingest_filelike_layer
from .marshal import import_kml_parser, optional_arguments



def parse_kwargs(*args, **kwargs):
    def wrapper(target):
        kwargs = {}
        form = import_kml_parser.parse_args()
        body = json.loads(form.get("json", "{}"))
        body.update(form)
        for key in form.keys():
            kwargs[key] = body.pop(key, None)
        kwargs["json"] = body
        target(**kwargs)
    return wrapper
        


@namespace.route("/kml/import")
class ImportKML(Resource):
    @namespace.doc("KML File import.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    @namespace.expect(import_kml_parser, validate=True)
    def post(self):
        form = import_kml_parser.parse_args()
        kwargs = {
            "file": form.file,
            "layer": form.layer,
        }
        body = json.loads(getattr(form, "json", "{}"))
        body.update(
            {key: getattr(form, key) for key in optional_arguments if getattr(form, key)}
        )
        for key in optional_arguments:
            kwargs[key] = body.pop(key, None)
        kwargs["json"] = body
        # kml = load_post_kml(form)
        # kml.to_csv("/home/rainmaker/Desktop/kml.csv")
        ingest_filelike_layer(**kwargs)
        return str(kwargs)
            # "columns": kml.columns.to_list(),
            # "shape": str(kml.head()),


@namespace.route("/kml/append")
class UpdateKML(Resource):
    @namespace.doc("KML File append.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    @namespace.expect(import_kml_parser, validate=True)
    def put(self):
        form = import_kml_parser.parse_args()
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
        form = import_kml_parser.parse_args()
        return {
            "endpoint": "POST geoserver/remove/kml",
            "form": f"{form}",
            "request": f"{request.__dict__}",
        }
