from flask_restx import reqparse
from werkzeug.datastructures import FileStorage


def form_maker(*args):
    """
    Crea un objeto RequestParser con los argumentos proporcionados.

    Args:
        *args: Argumentos a agregar al RequestParser.

    Returns:
        RequestParser: Objeto RequestParser configurado con los argumentos.

    """
    request_parser = reqparse.RequestParser()
    for arg in args:
        request_parser.add_argument(arg)
    return request_parser


base_arguments = {
    "layer": reqparse.Argument(
        "layer",
        dest="layer",
        location="form",
        type=str,
        required=True,
        help="Target layer name.",
    ),
    "style": reqparse.Argument(
        "style",
        dest="style",
        location="form",
        type=str,
        required=True,
        help="Target style name.",
    ),
    "file": reqparse.Argument(
        "file",
        dest="file",
        location="files",
        type=FileStorage,
        required=True,
        help="File to be imported.",
    ),
    "url": reqparse.Argument(
        "url",
        dest="file",
        location="form",
        type=str,
        required=True,
        help="File url to be imported.",
    ),
    "metadata": reqparse.Argument(
        "metadata",
        dest="json",
        location="form",
        type=str,
        required=False,
    ),
}


class badRequestException(Exception):
    pass


class serverErrorException(Exception):
    pass
