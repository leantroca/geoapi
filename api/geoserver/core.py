from typing import Optional, Union

# import geopandas
# from flask_restx.reqparse import ParseResult
from geoalchemy2 import functions as func
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from werkzeug.datastructures import FileStorage

from etc.config import settings
from models.tables import Geometries, Layers, Batches, Logs
from utils.geoserver_interface import Geoserver
from utils.kml_interface import KML
from utils.postgis_interface import PostGIS

postgis = PostGIS()
geoserver = Geoserver()


# def load_post_kml(form: ParseResult) -> geopandas.GeoDataFrame:
#     tablename = layername = form.layer.strip().replace(" ", "_").lower()
#     rows_appended = 0
#     postgis.drop_table(tablename, if_not_exists="ignore")
#     for chunk in read_kml(
#         data=form.file, chunksize=settings.DEFAULT_CHUNKSIZE, on_bad_lines="skip"
#     ):
#         for col in optional_arguments.keys():
#             chunk[col] = getattr(form, col)
#         rows_appended += chunk.shape[0]
#         print(f"[{rows_appended}]: {chunk['geometry']}")
#         postgis.create_table(
#             tablename=tablename,
#             data=chunk,
#             if_exists="append" if tablename in postgis.list_tables() else "replace",
#         )
#         print(f"Table {postgis.schema}.{tablename} created! ({rows_appended})")
#     geoserver.push_layer(layer=layername)
#     print(f"Layer {geoserver.workspace}:{layername} created!")

def keep_track(log:Logs=None, **kwargs):
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
    json: Optional[str] = None,
    log: Logs = None,
):
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
    log.message = "PostGIS view created."
    postgis.session.commit()
    # Import layer
    geoserver.push_layer(
        layer=layer,
        **postgis.bbox(layer),
    )
    log.message = "Geoserver layer created."
    postgis.session.commit()
    # Return
    return log


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
    json: Optional[str] = None,
):
    pass
