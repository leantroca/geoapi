import os
from typing import Optional, Union

from flask_restx import reqparse
from geoalchemy2 import functions as func
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models.tables import Batches, Geometries, Logs
from utils.config import settings
from utils.geoserver_interface import Geoserver
from utils.kml_interface import KML
from utils.postgis_interface import PostGIS

postgis = PostGIS()
geoserver = Geoserver()


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


def is_true(value):
    return value.lower() == "true"


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

batch_arguments = {
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

kml_read_error_handle = reqparse.Argument(
    "error_handle",
    dest="error_handle",
    location="form",
    type=str,
    required=False,
    default="fail",
    choices=["fail", "replace", "drop"],
)


class badRequestException(Exception):
    pass


class serverErrorException(Exception):
    pass


def temp_store(file: Union[str, list]) -> str:
    """
    Almacena temporalmente archivos subidos en una ubicación segura.

    Esta función recibe un archivo único o una lista de archivos (representados como
    strings u objetos FileStorage) y los guarda temporalmente en una ubicación segura
    definida por la variable settings.TEMP_BASE. Si se proporciona una lista de archivos,
    cada archivo se almacenará con un nombre único generado en función de su índice en la lista.

    Args:
        file (Union[str, list]): Ruta de un archivo único o lista de rutas de archivos
            o objetos FileStorage que serán almacenados temporalmente.

    Returns:
        str: Ruta de un archivo único o lista de rutas de archivos que apuntan a los
        archivos almacenados temporalmente.

    Notas:
        - Si se proporciona una ruta de archivo única, se convertirá en una lista que
          contiene esa ruta de archivo.
        - Si la entrada es una lista de objetos FileStorage, cada objeto se guardará
          en la ubicación temporal utilizando un nombre de archivo único.
    """
    if not isinstance(file, list):
        file = [file]
    for i, element in enumerate(file):
        if isinstance(element, FileStorage):
            file[i] = os.path.join(
                settings.TEMP_BASE, f"{i:04d}_{secure_filename(element.filename)}"
            )
            element.save(file[i])
    return file


def temp_remove(file: Union[str, list]) -> None:
    """
    Elimina archivos almacenados temporalmente de manera segura.

    Esta función toma una ruta de archivo única o una lista de rutas de archivos y
    elimina los archivos correspondientes si están almacenados temporalmente en la
    ubicación segura definida por la variable settings.TEMP_BASE.

    Args:
        file (Union[str, list]): Ruta de un archivo único o lista de rutas de archivos
            que serán eliminados si están almacenados temporalmente.

    Returns:
        None

    Notas:
        - Si se proporciona una ruta de archivo única, se convertirá en una lista que
          contiene esa ruta de archivo.
        - Los archivos se eliminarán solo si su ubicación está dentro de la carpeta
          definida por settings.TEMP_BASE, lo que asegura que solo se borren archivos
          temporales creados por la función temp_store.
        - Si ocurre un error durante el intento de eliminación de un archivo, se ignora
          silenciosamente.
    """
    if not isinstance(file, list):
        file = [file]
    for element in file:
        if isinstance(element, str) and os.path.dirname(element).startswith(
            settings.TEMP_BASE
        ):
            try:
                os.remove(element)
            except OSError:
                pass


def generate_batch(
    file: Union[str, list, FileStorage],
    obra: Optional[str] = None,
    operatoria: Optional[str] = None,
    provincia: Optional[str] = None,
    departamento: Optional[str] = None,
    municipio: Optional[str] = None,
    localidad: Optional[str] = None,
    estado: Optional[str] = None,
    descripcion: Optional[str] = None,
    cantidad: Optional[str] = None,
    categoria: Optional[str] = None,
    ente: Optional[str] = None,
    fuente: Optional[str] = None,
    json: Optional[dict] = None,
    error_handle: Optional[str] = "skip",
    log: Union[int, Logs] = None,
) -> Batches:
    """
    Genera un lote de datos a partir de un archivo KML o una lista de archivos KML.

    Args:
        file (Union[str, list, FileStorage]): Ruta de un archivo KML, lista de rutas de archivos KML
            o un objeto FileStorage.
        obra (Optional[str]): Obra del lote (opcional).
        operatoria (Optional[str]): Operatoria del lote (opcional).
        provincia (Optional[str]): Provincia del lote (opcional).
        departamento (Optional[str]): Departamento del lote (opcional).
        municipio (Optional[str]): Municipio del lote (opcional).
        localidad (Optional[str]): Localidad del lote (opcional).
        estado (Optional[str]): Estado del lote (opcional).
        descripcion (Optional[str]): Descripción del lote (opcional).
        cantidad (Optional[str]): Cantidad del lote (opcional).
        categoria (Optional[str]): Categoría del lote (opcional).
        ente (Optional[str]): Ente del lote (opcional).
        fuente (Optional[str]): Fuente del lote (opcional).
        json (Optional[dict]): JSON asociado al lote (opcional).
        error_handle (Optional[str]): Manejo de errores al procesar los anillos lineales
            (opcional, valor por defecto: "skip").
        log (Logs): Objeto Logs existente para mantener un registro de las operaciones (opcional).

    Returns:
        Batches: Objeto Batches que contiene los datos del lote generado.

    """
    if isinstance(log, int):
        log = postgis.get_log(id=log)
    generate_batch = Batches(
        obra=obra,
        operatoria=operatoria,
        provincia=provincia,
        departamento=departamento,
        municipio=municipio,
        localidad=localidad,
        estado=estado,
        descripcion=descripcion,
        cantidad=cantidad,
        categoria=categoria,
        ente=ente,
        fuente=fuente,
        json=json,
    )
    if not isinstance(file, list):
        file = [file]
    for element in file:
        kml = KML(file=element)
        kml.handle_linear_rings(errors=error_handle)
        try:
            for chunk in kml.read_kml(
                chunksize=settings.DEFAULT_CHUNKSIZE,  # on_bad_lines="skip"
            ):
                chunk.columns = map(str.lower, chunk.columns)
                for _, row in chunk.iterrows():
                    parsed_geometry = (
                        from_shape(row["geometry"], srid=postgis.coordsysid)
                        if row["geometry"].has_z
                        else func.ST_Force3D(
                            WKTElement(row["geometry"].wkt, srid=postgis.coordsysid)
                        )
                    )
                    generate_batch.geometries.append(
                        Geometries(
                            geometry=parsed_geometry,
                            name=row["name"],
                            description=row["description"],
                        )
                    )
        except ValueError as error:
            raise ValueError(
                ". ".join(
                    [
                        str(error).rstrip(". "),
                        "Verify file format. Try using parameter error_handle='replace' or 'drop'.",
                    ]
                )
            )
    return generate_batch
