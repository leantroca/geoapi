import json

from flask import request
from flask_restx import Resource
from werkzeug.utils import secure_filename

from . import namespace
from .core import kml_to_create_layer, kml_to_append_layer, keep_track
from .marshal import import_kml_parser


def parse_kwargs(parser):
    form = parser.parse_args()
    unpack = [arg.name for arg in parser.args if not arg.required]
    kwargs = {
        "file": form.file,
        "layer": secure_filename(form.layer),
    }
    body = json.loads(getattr(form, "json") or "{}")
    body.update(
        **{
            arg: getattr(form, arg)
            for arg in unpack
            if arg != "json" and getattr(form, arg) is not None
        }
    )
    for arg in unpack:
        kwargs[arg] = body.pop(arg, None)
    kwargs["json"] = body
    return {key: value for key, value in kwargs.items() if value is not None}


@namespace.route("/kml/form/create")
class KMLFormCreate(Resource):
    @namespace.doc("KML File import.")
    # @api.response(201, "Success", response_model)
    # @api.response(400, "Error", response_model)
    # @marshal_with(response_model)
    @namespace.expect(import_kml_parser, validate=True)
    def post(self):
        log = keep_track(
            endpoint="/geoserver/kml/form/create",
            status="200",
            message="Received.",
        )
        kml_to_create_layer(**parse_kwargs(import_kml_parser), log=log)
        return (log.record, log.status)


@namespace.route("/kml/form/append")
class KMLFormAppend(Resource):
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
