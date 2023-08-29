import os
from typing import Optional, Union

from utils.config import settings
from geoalchemy2 import functions as func
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api.logger import core_exception_logger
from models.tables import Batches, Geometries, Layers, Logs
from utils.geoserver_interface import Geoserver
from utils.kml_interface import KML
from utils.postgis_interface import PostGIS

postgis = PostGIS()
geoserver = Geoserver()


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


def verify_layer_exists(layer: str):
    if layer not in geoserver.list_layers():
        raise ValueError(f"Layer {layer} doesn't exist on Geoserver.")
    if layer not in postgis.list_layers():
        raise ValueError(f"Layer {layer} doesn't exist on Postgis.")


def verify_layer_not_exists(layer: str):
    if layer in geoserver.list_layers():
        raise ValueError(f"Layer '{layer}' already exists on Geoserver.")
    if layer in postgis.list_layers():
        raise ValueError(f"Layer '{layer}' already exists on Postgis.")


@core_exception_logger
def kml_to_create_layer(
    file: Union[str, FileStorage],
    layer: str,
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
    log: Logs = None,
) -> None:
    """
    Convierte un archivo KML en una capa en GeoServer y la ingresa en la base de datos de PostGIS.

    Args:
        file (Union[str, FileStorage]): Ruta de un archivo KML o un objeto FileStorage.
        layer (str): Nombre de la capa en GeoServer.
        obra (Optional[str]): Obra asociada a la capa (opcional).
        operatoria (Optional[str]): Operatoria asociada a la capa (opcional).
        provincia (Optional[str]): Provincia asociada a la capa (opcional).
        departamento (Optional[str]): Departamento asociado a la capa (opcional).
        municipio (Optional[str]): Municipio asociado a la capa (opcional).
        localidad (Optional[str]): Localidad asociada a la capa (opcional).
        estado (Optional[str]): Estado asociado a la capa (opcional).
        descripcion (Optional[str]): Descripción asociada a la capa (opcional).
        cantidad (Optional[str]): Cantidad asociada a la capa (opcional).
        categoria (Optional[str]): Categoría asociada a la capa (opcional).
        ente (Optional[str]): Ente asociado a la capa (opcional).
        fuente (Optional[str]): Fuente asociada a la capa (opcional).
        json (Optional[dict]): JSON asociado a la capa (opcional).
        error_handle (Optional[str]): Manejo de errores al procesar los anillos lineales
            (opcional, valor por defecto: "skip").
        log (Logs): Objeto Logs existente para mantener un registro de las operaciones (opcional).

    Returns:
        None

    """
    log = log or Logs()
    verify_layer_not_exists(layer=layer)
    new_layer = Layers(
        name=layer,
    )
    postgis.session.add(new_layer)
    new_batch = generate_batch(
        file=file,
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
        error_handle=error_handle,
    )
    new_layer.batches.append(new_batch)
    postgis.session.add(new_batch)
    log.batch_id = new_batch.id
    log.message = "PostGIS KML ingested."
    postgis.session.commit()
    # Create View
    postgis.create_view(layer)
    log.message_append("PostGIS view created.")
    postgis.session.commit()
    # Import layer
    geoserver.push_layer(
        layer=layer,
        **postgis.bbox(layer),
    )
    log.message_append("Geoserver layer created.")
    postgis.session.commit()


@core_exception_logger
def kml_to_append_layer(
    file: Union[str, FileStorage],
    layer: str,
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
    log: Logs = None,
) -> None:
    """
    Agrega datos de un archivo KML a una capa existente en GeoServer y los ingresa en la base de datos de PostGIS.

    Args:
        file (Union[str, FileStorage]): Ruta de un archivo KML o un objeto FileStorage.
        layer (str): Nombre de la capa en GeoServer.
        obra (Optional[str]): Obra asociada a la capa (opcional).
        operatoria (Optional[str]): Operatoria asociada a la capa (opcional).
        provincia (Optional[str]): Provincia asociada a la capa (opcional).
        departamento (Optional[str]): Departamento asociado a la capa (opcional).
        municipio (Optional[str]): Municipio asociado a la capa (opcional).
        localidad (Optional[str]): Localidad asociada a la capa (opcional).
        estado (Optional[str]): Estado asociado a la capa (opcional).
        descripcion (Optional[str]): Descripción asociada a la capa (opcional).
        cantidad (Optional[str]): Cantidad asociada a la capa (opcional).
        categoria (Optional[str]): Categoría asociada a la capa (opcional).
        ente (Optional[str]): Ente asociado a la capa (opcional).
        fuente (Optional[str]): Fuente asociada a la capa (opcional).
        json (Optional[dict]): JSON asociado a la capa (opcional).
        error_handle (Optional[str]): Manejo de errores al procesar los anillos lineales
            (opcional, valor por defecto: "skip").
        log (Logs): Objeto Logs existente para mantener un registro de las operaciones (opcional).

    Returns:
        None

    """
    log = log or Logs()
    verify_layer_exists(layer=layer)
    append_layer = postgis.get_layer(name=layer)
    new_batch = generate_batch(
        file=file,
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
        error_handle=error_handle,
    )
    append_layer.batches.append(new_batch)
    postgis.session.add(new_batch)
    log.batch_id = new_batch.id
    log.message = "PostGIS KML ingested."
    postgis.session.commit()
    geoserver.delete_layer(
        layer=layer,
    )
    geoserver.push_layer(
        layer=layer,
        **postgis.bbox(layer),
    )
    log.message_append("Geoserver layer updated.")
    postgis.session.commit()


@core_exception_logger
def delete_layer(
    layer: str,
    delete_geometries: Optional[bool] = False,
    json: Optional[dict] = None,
    error_handle: Optional[str] = "ignore",
    log: Optional[Logs] = None,
) -> None:
    """
    Elimina una capa y sus datos asociados de GeoServer y PostGIS.

    Args:
        layer (str): Nombre de la capa a eliminar.
        delete_geometries (Optional[bool]): Indica si se deben eliminar también las geometrías de la capa
            en PostGIS (opcional, valor por defecto: False).
        json (Optional[dict]): JSON asociado a la capa (opcional).
        error_handle (Optional[str]): Manejo de errores al eliminar la capa en GeoServer
            (opcional, valor por defecto: "ignore").
        log (Optional[Logs]): Objeto Logs existente para mantener un registro de las operaciones (opcional).

    Returns:
        None

    """
    log = log or Logs()
    geoserver.delete_layer(layer=layer, if_not_exists=error_handle)
    log.message = "Geoserver layer deleted."
    postgis.session.commit()
    postgis.drop_view(layer=layer, if_not_exists=error_handle, cascade=True)
    log.message_append("View deleted.")
    postgis.session.commit()
    postgis.drop_layer(
        layer=layer, if_not_exists=error_handle, cascade=delete_geometries
    )
    log.message_append(
        f"Postgis layer {'and geometries ' if delete_geometries else ''}deleted."
    )
    postgis.session.commit()


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


def get_log(id: Union[int, Logs]):
    """
    Recupera un registro de registro o una lista de registros según el ID proporcionado.

    Esta función toma un ID de registro único o un objeto Logs y recupera el registro
    correspondiente utilizando el módulo postgis.get_log si se proporciona un ID entero,
    o simplemente devuelve el objeto Logs si ya es proporcionado.

    Args:
        id (Union[int, Logs]): Un ID de registro único o un objeto Logs que se utilizará
            para recuperar el registro o se devolverá directamente.

    Returns:
        El registro de registro correspondiente si se proporciona un ID entero, o el
        objeto Logs proporcionado.

    Notas:
        - Si se proporciona un objeto Logs en lugar de un ID, se devolverá ese objeto
          sin realizar ninguna operación adicional.
        - Si se proporciona un ID entero, se utilizará el módulo postgis.get_log para
          recuperar el registro de registro correspondiente.
    """
    return postgis.get_log(id=id) if isinstance(id, int) else id


def get_log_response(id: Union[int, Logs]):
    """TBD"""
    log = get_log(id=id)
    return log.record, log.status
