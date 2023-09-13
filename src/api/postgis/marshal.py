import json

from flask_restx import reqparse
from werkzeug.utils import secure_filename

from api.utils import base_arguments, batch_arguments, kml_read_error_handle, form_maker
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
    kwargs = {}
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



kml_to_geometries_parser = form_maker(
    base_arguments["file"],
    *batch_arguments.values(),
    base_arguments["metadata"],
    kml_read_error_handle,
)