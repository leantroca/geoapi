import geopandas
from flask_restx.reqparse import ParseResult

from api.config import settings
from utils.geoserver_interface import Geoserver
from utils.kml_interface import read_kml
from utils.postgis_interface import PostGIS

from .marshal import optional_arguments

postgis = PostGIS()
geoserver = Geoserver()


def load_post_kml(form: ParseResult) -> geopandas.GeoDataFrame:
    tablename = layername = form.layer.strip().replace(" ", "_").lower()
    rows_appended = 0
    postgis.drop_table(tablename, if_not_exists="ignore")
    for chunk in read_kml(
        data=form.file, chunksize=settings.DEFAULT_CHUNKSIZE, on_bad_lines="skip"
    ):
        for col in optional_arguments.keys():
            chunk[col] = getattr(form, col)
        rows_appended += chunk.shape[0]
        print(f"[{rows_appended}]: {chunk['geometry']}")
        postgis.create_table(
            tablename=tablename,
            data=chunk,
            if_exists="append" if tablename in postgis.list_tables() else "replace",
        )
        print(f"Table {postgis.schema}.{tablename} created! ({rows_appended})")
    geoserver.push_layer(layer=layername)
    print(f"Layer {geoserver.workspace}:{layername} created!")
