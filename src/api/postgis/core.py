from typing import List, Optional, Union

from werkzeug.datastructures import FileStorage

from api.logger import Logger, core_exception_logger
from api.utils import generate_batch
from utils.geoserver_interface import Geoserver
from utils.postgis_interface import PostGIS

geoserver = Geoserver()


@core_exception_logger
def kml_to_create_batch(
    file: Union[str, FileStorage],
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
    logger: Optional[Logger] = None,
    **kwargs,
) -> None:
    """
    Convierte un archivo KML en geometrías para la base de datos de PostGIS.

    Args:
        file (Union[str, FileStorage]): Ruta de un archivo KML o un objeto FileStorage.
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
    with PostGIS() as postgis:
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
        postgis.session.add(new_batch)
        postgis.session.flush()
        batch_id = new_batch.id
    # Fin de operaciones en DB.
    if logger:
        logger.keep_track(
            batch_id=batch_id,
            message_append="PostGIS KML ingested.",
        )


@core_exception_logger
def view_push_to_layer(
    layer: str,
    view: Optional[str] = None,
    error_handle: str = "fail",
    logger: Optional[Logger] = None,
    **kwargs,
):
    """
    Crea una nueva capa en Geoserver y registra la acción en el log.

    Args:
    - layer (str): Nombre de la capa a crear en Geoserver.
    - error_handle (str): Manejo de errores si la capa ya existe ("fail" o "replace").
    - log (Logs): Objeto de log opcional para registrar la acción.

    Keyword Args:
    - kwargs: Otros argumentos opcionales.

    """
    with PostGIS() as postgis:
        new_layer = postgis.get_or_create_layer(name=layer)
        postgis.session.add(new_layer)
    # Fin de operaciones en DB.
    if logger:
        logger.keep_track(
            message_append="View created.",
        )
    geoserver.push_layer(
        layer=layer,
        view=view,
        if_exists=error_handle,
        **postgis.bbox(view),
    )
    if logger:
        logger.keep_track(
            message_append="Geoserver layer created.",
        )


@core_exception_logger
def delete_geometries(
    ids: Union[int, List[int]],
    error_handle: str = "fail",
    logger: Optional[Logger] = None,
    *args,
    **kwargs,
):
    """
    Elimina geometrías de PostGIS y registra la acción en el log.

    Args:
    - ids (Union[int, List[int]]): ID o lista de IDs de geometrías a eliminar.
    - error_handle (str): Manejo de errores ("fail" o "replace").
    - log (Optional[int]): Objeto de log opcional para registrar la acción.

    Keyword Args:
    - args: Argumentos posicionales adicionales.
    - kwargs: Otros argumentos opcionales.

    """
    with PostGIS() as postgis:
        count = postgis.drop_geometries(ids)
    if logger:
        logger.keep_track(
            message_append=f"Postgis deleted {count} geometries.",
        )


@core_exception_logger
def delete_batches(
    ids: Union[int, List[int]],
    cascade: bool = False,
    error_handle: str = "fail",
    logger: Optional[Logger] = None,
    *args,
    **kwargs,
):
    """
    Elimina lotes de geometrías en PostGIS y registra la acción en el log.

    Args:
    - ids (Union[int, List[int]]): ID o lista de IDs de lotes a eliminar.
    - cascade (bool): Indica si se deben eliminar en cascada las dependencias.
    - error_handle (str): Manejo de errores ("fail" o "replace").
    - log (Optional[int]): Objeto de log opcional para registrar la acción.

    Keyword Args:
    - args: Argumentos posicionales adicionales.
    - kwargs: Otros argumentos opcionales.

    """
    with PostGIS() as postgis:
        count = postgis.drop_batches(ids, cascade=cascade)
    if logger:
        logger.keep_track(
            message_append=f"Postgis deleted {count} geometries.",
        )
