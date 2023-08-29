import json

from flask_restx import reqparse
from werkzeug.utils import secure_filename

from api.utils import base_arguments, form_maker
from utils.general import clean_nones


def parse_kwargs(parser):
    """
    Analiza los argumentos proporcionados por un parser y los devuelve como un diccionario de kwargs.

    Args:
        parser (RequestParser): Parser de Flask-RESTX.

    Returns:
        dict: Diccionario de kwargs generado a partir de los argumentos.

    Raises:
        TypeError: Error al analizar los argumentos.
    """
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
        kwargs["file"] = [
            element.strip(" ,\"'[](){{}}") for element in kwargs["file"].split(",")
        ]
    kwargs["json"] = body
    return clean_nones(kwargs)


"""
# Look only in the POST body
parser.add_argument('name', type=int, location='form')

# Look only in the querystring
parser.add_argument('PageSize', type=int, location='args')

# From the request headers
parser.add_argument('User-Agent', location='headers')

# From http cookies
parser.add_argument('session_id', location='cookies')

# From file uploads
parser.add_argument('picture', type=werkzeug.datastructures.FileStorage,
   location='files')

# Docs on argument construction in:
# https://flask-restx.readthedocs.io/en/latest/api.html#module-flask_restx.reqparse
"""

kml_arguments = {
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

kml_error_handle = reqparse.Argument(
    "error_handle",
    dest="error_handle",
    location="form",
    type=str,
    required=False,
    default="fail",
    choices=["fail", "replace", "drop"],
)

layer_error_handle = reqparse.Argument(
    "error_handle",
    dest="error_handle",
    location="form",
    type=str,
    required=False,
    default="fail",
    choices=["fail", "ignore"],
)

delete_geometries = reqparse.Argument(
    "delete_geometries",
    dest="delete_geometries",
    location="form",
    type=bool,
    required=False,
    default=True,
)


upload_kml_parser = form_maker(
    base_arguments["file"],
    base_arguments["layer"],
    *kml_arguments.values(),
    base_arguments["metadata"],
    kml_error_handle,
)

download_kml_parser = form_maker(
    base_arguments["url"],
    base_arguments["layer"],
    *kml_arguments.values(),
    base_arguments["metadata"],
    kml_error_handle,
)

delete_layer_parser = form_maker(
    base_arguments["layer"],
    delete_geometries,
    base_arguments["metadata"],
    layer_error_handle,
)
