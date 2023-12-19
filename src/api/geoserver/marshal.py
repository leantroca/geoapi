import json

from flask_restx import reqparse
from werkzeug.utils import secure_filename

from api.utils import (
    base_arguments,
    batch_arguments,
    form_maker,
    is_true,
    kml_read_error_handle,
)
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
        if arg in ["delete_geometries"]:
            # Handle booleans as intended.
            kwargs[arg] = is_true(body.pop(arg, None))
        else:
            # Handles everything else.
            kwargs[arg] = body.pop(arg, None)
    if [arg for arg in parser.args if arg.name == "url"]:
        kwargs["file"] = [
            element.strip(" ,\"'[](){{}}") for element in kwargs["file"].split(",")
        ]
    kwargs["json"] = body
    return clean_nones(kwargs)


# kml_error_handle = reqparse.Argument(
#     "error_handle",
#     dest="error_handle",
#     location="form",
#     type=str,
#     required=False,
#     default="fail",
#     choices=["fail", "replace", "drop"],
# )

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
    type=str,
    required=False,
    default="false",
    choices=["true", "false"],
)


upload_kml_parser = form_maker(
    base_arguments["file"],
    base_arguments["layer"],
    *batch_arguments.values(),
    base_arguments["metadata"],
    kml_read_error_handle,
)

download_kml_parser = form_maker(
    base_arguments["url"],
    base_arguments["layer"],
    *batch_arguments.values(),
    base_arguments["metadata"],
    kml_read_error_handle,
)

delete_layer_parser = form_maker(
    base_arguments["layer"],
    delete_geometries,
    base_arguments["metadata"],
    layer_error_handle,
)
