from typing import Optional, Union

from werkzeug.datastructures import FileStorage

from utils.postgis_interface import PostGIS
from api.logger import core_exception_logger, get_log
from api.utils import generate_batch
from models.tables import Layers, Logs
from utils.geoserver_interface import Geoserver

geoserver = Geoserver()


def verify_layer_exists(layer: str):
    if layer not in geoserver.list_layers():
        raise ValueError(f"Layer {layer} doesn't exist on Geoserver.")
    with PostGIS() as postgis:
        if layer not in postgis.list_layers():
            raise ValueError(f"Layer {layer} doesn't exist on Postgis.")


def verify_layer_not_exists(layer: str):
    if layer in geoserver.list_layers():
        raise ValueError(f"Layer '{layer}' already exists on Geoserver.")
    with PostGIS() as postgis:
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
    with PostGIS() as postgis:
        log = get_log(log) if isinstance(log, int) else log or Logs()
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
    with PostGIS() as postgis:
        log = get_log(log) if isinstance(log, int) else log or Logs()
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
    with PostGIS() as postgis:
        log = get_log(log) if isinstance(log, int) else log or Logs()
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
