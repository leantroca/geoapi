import os
import re
from typing import Optional, Union, List

from geoalchemy2 import functions as func
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api.logger import core_exception_logger, get_log
from api.utils import generate_batch
from api.celery import postgis
from models.tables import Batches, Geometries, Layers, Logs
from utils.config import settings
from utils.geoserver_interface import Geoserver
from utils.kml_interface import KML

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
    log: Logs = None,
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
    log = get_log(log) if isinstance(log, int) else log or Logs()
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
    log.batch = new_batch
    log.message = "PostGIS KML ingested."
    postgis.session.commit()


@core_exception_logger
def view_push_to_layer(
    layer: str,
    error_handle: str = "fail",
    log: Logs = None,
    **kwargs,
):
    """
    TBD
    """
    log = get_log(log) if isinstance(log, int) else log or Logs()
    new_layer = postgis.get_or_create_layer(name=layer)
    postgis.session.add(new_layer)
    geoserver.push_layer(
        layer=layer,
        if_exists=error_handle,
        **postgis.bbox(layer),
    )
    log.message_append("Geoserver layer created.")
    postgis.session.commit()


@core_exception_logger
def delete_geometries(
    geometry_id: Union[int, List[int]],
    error_handle: str = "fail",
    log: Optional[int] = None,
    *args,
    **kwargs,
):
    """TBD"""
    log = get_log(log) if isinstance(log, int) else log or Logs()
    count = postgis.drop_geometries(geometry_id)
    log.message = f"Postgis deleted {count} geometries."
    postgis.session.commit()


@core_exception_logger
def delete_batches(
    batch_id: Union[int, List[int]],
    cascade: bool = False,
    error_handle: str = "fail",
    log: Optional[int] = None,
    *args,
    **kwargs,
):
    """TBD"""
    log = get_log(log) if isinstance(log, int) else log or Logs()
    count = postgis.drop_batches(batch_id, cascade=cascade)
    log.message = f"Postgis deleted {count} geometries."
    postgis.session.commit()

