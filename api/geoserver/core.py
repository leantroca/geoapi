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
    log: Logs = None,
) -> None:
    # Update Logs #################
    log = log or Logs()
    log.message = "Processing."
    postgis.session.commit()
    ###############################
    new_layer = Layers(
        name=layer,
    )
    new_batch = Batches(
        layer=new_layer,
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
    # Update Logs #################
    postgis.session.add_all([new_batch, new_layer])
    log.batch = new_batch
    ###############################
    kml = KML(file=file)
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
            postgis.session.add(
                Geometries(
                    geometry=parsed_geometry,
                    name=row["name"],
                    description=row["description"],
                    batch=new_batch,
                )
            )
    log.message = "PostGIS KML ingested."
    # Commit geometries
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
) -> None:
    pass


def delete_layer(
    layer: str,
    delete_geometries: Optional[bool] = False,
    json: Optional[dict] = None,
    log: Optional[Logs] = None,
) -> None:
    log = log or Logs()
    geoserver.delete_layer(layer=layer, if_not_exists="ignore")
    log.message = "Geoserver layer deleted."
    postgis.session.commit()
    postgis.drop_view(layer=layer, if_not_exists="ignore", cascade=True)
    log.message_append("View deleted.")
    postgis.session.commit()
    postgis.drop_layer(layer=layer, if_not_exists="ignore", cascade=delete_geometries)
    log.message_append(
        f"Postgis layer {'and geometries ' if delete_geometries else ''}deleted."
    )
    postgis.session.commit()
