from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

# # Look only in the POST body
# parser.add_argument('name', type=int, location='form')
#
# # Look only in the querystring
# parser.add_argument('PageSize', type=int, location='args')
#
# # From the request headers
# parser.add_argument('User-Agent', location='headers')
#
# # From http cookies
# parser.add_argument('session_id', location='cookies')
#
# # From file uploads
# parser.add_argument('picture', type=werkzeug.datastructures.FileStorage,
#    location='files')
#
# Docs on argument construction in:
# https://flask-restx.readthedocs.io/en/latest/api.html#module-flask_restx.reqparse

file = reqparse.Argument(
    "KML File",
    dest="file",
    location="files",
    type=FileStorage,
    required=True,
    help="KML file to be imported.",
)

layer = reqparse.Argument(
    "Target Layer Name",
    dest="layer",
    location="form",
    type=str,
    required=True,
    help="Target layer name to be created.",
)

optional_arguments = {
    "obra": reqparse.Argument(
        "obra",
        dest="obra",
        location="form",
        type=str,
        required=False,
    ),
    "operatoria": reqparse.Argument(
        "operatoria",
        dest="operatoria",
        location="form",
        type=str,
        required=False,
    ),
    "provincia": reqparse.Argument(
        "provincia",
        dest="provincia",
        location="form",
        type=str,
        required=False,
    ),
    "departamento": reqparse.Argument(
        "departamento",
        dest="departamento",
        location="form",
        type=str,
        required=False,
    ),
    "municipio": reqparse.Argument(
        "municipio",
        dest="municipio",
        location="form",
        type=str,
        required=False,
    ),
    "localidad": reqparse.Argument(
        "localidad",
        dest="localidad",
        location="form",
        type=str,
        required=False,
    ),
    "estado": reqparse.Argument(
        "estado",
        dest="estado",
        location="form",
        type=str,
        required=False,
    ),
    "descripcion": reqparse.Argument(
        "descripcion",
        dest="descripcion",
        location="form",
        type=str,
        required=False,
    ),
    "cantidad": reqparse.Argument(
        "cantidad",
        dest="cantidad",
        location="form",
        type=str,
        required=False,
    ),
    "categoria": reqparse.Argument(
        "categoria",
        dest="categoria",
        location="form",
        type=str,
        required=False,
    ),
    "ente": reqparse.Argument(
        "ente",
        dest="ente",
        location="form",
        type=str,
        required=False,
    ),
    "fuente": reqparse.Argument(
        "fuente",
        dest="fuente",
        location="form",
        type=str,
        required=False,
    ),
}

json_metadata = reqparse.Argument(
    "json",
    dest="json",
    location="form",
    type=str,
    required=False,
)

def form_maker(*args):
    request_parser = reqparse.RequestParser()
    for arg in args:
        request_parser.add_argument(arg)
    return request_parser


import_kml_parser = form_maker(
    file,
    layer,
    *optional_arguments.values(),
    json_metadata,
)

# from . import namespace

# body_model: namespace.model(

# )