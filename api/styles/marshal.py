from api.utils import form_maker, base_arguments
from flask_restx import reqparse
from werkzeug.utils import secure_filename
import json
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
    # Registra argumentos.
    form = parser.parse_args()
    # Separa entre keys obligatorias y opcionales.
    required = [arg.dest for arg in parser.args if arg.required]
    optional = [arg.dest for arg in parser.args if not arg.required]
    # Crea una nomenclatura segura para el estilo.
    kwargs = {
        "style": secure_filename(form.style),
    }
    # Extrae argumentos obligatorios.
    for arg in required:
        kwargs[arg] = getattr(form, arg)
    # Extrae argumentos contenida dentro de la metadata.
    body = json.loads(getattr(form, "json") or "{}")
    # Sobreescribe metadata con argumentos opcionales del form.
    body.update(
        **{
            arg: getattr(form, arg)
            for arg in optional
            if arg != "json" and getattr(form, arg) is not None
        }
    )
    # Deja en metadata solo argumentos no esperados.
    for arg in optional:
        kwargs[arg] = body.pop(arg, None)
    # Asigna argumentos no esperados a la metadata.
    kwargs["json"] = body
    return clean_nones(kwargs)


error_create_existing_style = reqparse.Argument(
    "error_handle",
    dest="error_handle",
    location="form",
    type=str,
    required=False,
    default="fail",
    choices=["fail", "replace", "ignore"],
)

error_delete_unexisting_style = reqparse.Argument(
    "error_handle",
    dest="error_handle",
    location="form",
    type=str,
    required=False,
    default="fail",
    choices=["fail", "cascade"],
)


upload_style_parser = form_maker(
    base_arguments["file"],
    base_arguments["style"],
    error_create_existing_style,
    base_arguments["metadata"],
)

assign_style_parser = form_maker(
    base_arguments["style"],
    base_arguments["layer"],
    base_arguments["metadata"],
)

delete_style_parser = form_maker(
    base_arguments["style"],
    error_delete_unexisting_style,
    base_arguments["metadata"],
)