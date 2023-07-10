


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


file = reqparse.Argument(
    "file",
    dest="file",
    location="files",
    type=FileStorage,
    required=True,
    help="KML file to be imported.",
)

url = reqparse.Argument(
    "url",
    dest="file",
    location="form",
    type=str,
    required=True,
    help="KML file url to be imported.",
)

layer = reqparse.Argument(
    "layer",
    dest="layer",
    location="form",
    type=str,
    required=True,
    help="Target layer name to be created.",
)

upload_sld_parser = form_maker(
    file,
    layer,
    *kml_arguments.values(),
    metadata,
    kml_error_handle,
)