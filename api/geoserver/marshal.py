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

# username = reqparse.Argument(
#     "Geoserver Username",
#     dest="user",
#     location="form",
#     type=str,
#     required=True,
#     help="Your username for wms.minhabitat.gob.ar.",
# )

# password = reqparse.Argument(
#     "Geoserver Password",
#     dest="pass",
#     location="form",
#     type=str,
#     required=True,
#     help="Your password for wms.minhabitat.gob.ar.",
# )

optional_arguments = {
    "obra_id": reqparse.Argument(
        "obra_id",
        dest="obra_id",
        location="form",
        type=str,
        required=False,
    ),
    "obra_operatoria": reqparse.Argument(
        "obra_operatoria",
        dest="obra_operatoria",
        location="form",
        type=str,
        required=False,
    ),
    "obra_provincia": reqparse.Argument(
        "obra_provincia",
        dest="obra_provincia",
        location="form",
        type=str,
        required=False,
    ),
    "obra_departamento": reqparse.Argument(
        "obra_departamento",
        dest="obra_departamento",
        location="form",
        type=str,
        required=False,
    ),
    "obra_municipio": reqparse.Argument(
        "obra_municipio",
        dest="obra_municipio",
        location="form",
        type=str,
        required=False,
    ),
    "obra_localidad": reqparse.Argument(
        "obra_localidad",
        dest="obra_localidad",
        location="form",
        type=str,
        required=False,
    ),
    "obra_estado": reqparse.Argument(
        "obra_estado",
        dest="obra_estado",
        location="form",
        type=str,
        required=False,
    ),
    "obra_descripción": reqparse.Argument(
        "obra_descripción",
        dest="obra_descripción",
        location="form",
        type=str,
        required=False,
    ),
    "obra_cantidad": reqparse.Argument(
        "obra_cantidad",
        dest="obra_cantidad",
        location="form",
        type=str,
        required=False,
    ),
    "obra_categoría": reqparse.Argument(
        "obra_categoría",
        dest="obra_categoría",
        location="form",
        type=str,
        required=False,
    ),
    "obra_ente": reqparse.Argument(
        "obra_ente",
        dest="obra_ente",
        location="form",
        type=str,
        required=False,
    ),
    "obra_fuente": reqparse.Argument(
        "obra_fuente",
        dest="obra_fuente",
        location="form",
        type=str,
        required=False,
    ),
}


def form_maker(*args):
    request_parser = reqparse.RequestParser()
    for arg in args:
        request_parser.add_argument(arg)
    return request_parser


import_kml_parser = form_maker(
    file,
    layer,
    *optional_arguments.values(),
)
