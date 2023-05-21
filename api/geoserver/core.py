from typing import Optional, Union

# import geopandas
# from flask_restx.reqparse import ParseResult
from geoalchemy2 import functions as func
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from werkzeug.datastructures import FileStorage

from etc.config import settings
from models.tables import Batches, Geometries, Layers, Logs
from utils.geoserver_interface import Geoserver
from utils.kml_interface import KML
from utils.postgis_interface import PostGIS

from requests.exceptions import HTTPError, ConnectionError

postgis = PostGIS()
geoserver = Geoserver()


def keep_track(log: Logs = None, **kwargs):
    if log is None:
        log = Logs()
        postgis.session.add(log)
    log.update(**kwargs)
    postgis.session.commit()
    return log


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
    if not log:
        log = Logs(message="Processing.", status=200)
        postgis.session.add(log)
        postgis.session.commit()
    if layer in geoserver.list_layers():
        log.message = f"Layer {layer} already exist."
        log.status = 400
        return
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
    log.batch = new_batch
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
    if not log:
        log = Logs(message="Processing.", status=200)
        postgis.session.add(log)
        postgis.session.commit()
    if layer not in geoserver.list_layers():
        log.message = f"Layer {layer} doesn't exist."
        log.status = 400
        return
    append_layer = postgis.get_layer(name=layer)
    try:
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
    except ValueError as error:
        log.message = str(error)
        log.message_append("Verify file format. Try using parameter error_handle='replace' or 'drop'.")
        log.status = 400
        return
    except Exception as error:
        log.message = str(error)
        log.status = 400
        return
    append_layer.batches.append(new_batch)
    postgis.session.add(new_batch)
    log.batch = new_batch
    log.message = "PostGIS KML ingested."
    postgis.session.commit()
    # Create View
    if layer not in postgis.list_views():
        postgis.create_view(layer)
        log.message_append("PostGIS view created.")
        postgis.session.commit()
    # Import layer
    geoserver.delete_layer(
        layer=layer,
    )
    geoserver.push_layer(
        layer=layer,
        **postgis.bbox(layer),
    )
    log.message_append("Geoserver layer updated.")
    postgis.session.commit()


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
    log: Logs = None,
) -> Batches:
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
    return generate_batch


def delete_layer(
    layer: str,
    delete_geometries: Optional[bool] = False,
    json: Optional[dict] = None,
    layer_error_handle: Optional[str] = "ignore",
    log: Optional[Logs] = None,
) -> None:
    if not log:
        log = Logs(message="Processing.", status=200)
        postgis.session.add(log)
        postgis.session.commit()
    try:
        geoserver.delete_layer(layer=layer, if_not_exists=layer_error_handle)
    except Exception as error:
        log.message = str(error)
        log.status = 400
        return
    log.message = "Geoserver layer deleted."
    postgis.session.commit()
    postgis.drop_view(layer=layer, if_not_exists=layer_error_handle, cascade=True)
    log.message_append("View deleted.")
    postgis.session.commit()
    postgis.drop_layer(layer=layer, if_not_exists=layer_error_handle, cascade=delete_geometries)
    log.message_append(
        f"Postgis layer {'and geometries ' if delete_geometries else ''}deleted."
    )
    postgis.session.commit()
