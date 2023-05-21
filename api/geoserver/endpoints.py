import json

from flask_restx import Resource
from werkzeug.utils import secure_filename

from . import namespace
from .core import delete_layer, keep_track, kml_to_append_layer, kml_to_create_layer
from .marshal import delete_layer_parser, upload_kml_parser, download_kml_parser


# TODO: Mover esto a .marshal.
def parse_kwargs(parser):
    form = parser.parse_args()
    required = [arg.dest for arg in parser.args if arg.required]
    optional = [arg.dest for arg in parser.args if not arg.required]
    kwargs = {
        "layer": secure_filename(form.layer),
    }
    for arg in required:
        kwargs[arg] = getattr(form, arg)
    body = json.loads(getattr(form, "json") or "{}")
    body.update(
        **{
            arg: getattr(form, arg)
            for arg in optional
            if arg != "json" and getattr(form, arg) is not None
        }
    )
    for arg in optional:
        kwargs[arg] = body.pop(arg, None)
    if [arg for arg in parser.args if arg.name == "url"]:
        kwargs["file"] = [element.strip(" ,\"\'[](){{}}") for element in kwargs["file"].split(",")]
    kwargs["json"] = body
    return {key: value for key, value in kwargs.items() if value is not None}


@namespace.route("/kml/form/create")
class KMLFormCreate(Resource):
    @namespace.doc("KML File import.")
    @namespace.expect(upload_kml_parser, validate=True)
    def post(self):
        kwargs = parse_kwargs(upload_kml_parser)
        log = keep_track(
            endpoint="/geoserver/kml/form/create",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_create_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/kml/form/append")
class KMLFormAppend(Resource):
    @namespace.doc("KML File ingest.")
    @namespace.expect(upload_kml_parser, validate=True)
    def put(self):
        kwargs = parse_kwargs(upload_kml_parser)
        log = keep_track(
            endpoint="/geoserver/kml/form/append",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_append_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/url/form/create")
class KMLFormCreate(Resource):
    @namespace.doc("KML URL ingest.")
    @namespace.expect(download_kml_parser, validate=True)
    def post(self):
        kwargs = parse_kwargs(download_kml_parser)
        log = keep_track(
            endpoint="/geoserver/url/form/create",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_create_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/url/form/append")
class KMLFormAppend(Resource):
    @namespace.doc("KML URL append.")
    @namespace.expect(download_kml_parser, validate=True)
    def put(self):
        kwargs = parse_kwargs(download_kml_parser)
        log = keep_track(
            endpoint="/geoserver/kml/form/append",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_append_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/layer/form/delete")
class DeleteLayer(Resource):
    @namespace.doc("KML File removal.")
    @namespace.expect(delete_layer_parser, validate=True)
    def delete(self):
        kwargs = parse_kwargs(delete_layer_parser)
        log = keep_track(
            endpoint="/geoserver/layer/form/delete",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        delete_layer(**kwargs, log=log)
        return (log.record, log.status)