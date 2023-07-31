from api.logger import core_exception_logger, debug_metadata, keep_track
from utils.sld_interface import SLD
from utils.geoserver_interface import Geoserver
from utils.postgis_interface import PostGIS
from typing import Union, Literal
from models.tables import Logs
from werkzeug.datastructures import FileStorage
from requests.exceptions import HTTPError


geoserver = Geoserver()
postgis = PostGIS()


@core_exception_logger
def push_sld_to_style(
    file: Union[str, FileStorage],
    style: str,
    error_handle: Literal["fail", "replace", "ignore"] = "fail",
    log: Union[int, Logs] = None,
):
    """TBD"""
    sld = SLD(file)
    try:
        geoserver.push_style(
            style=style,
            data=sld.read(),
            if_exists=error_handle,
        )
    except HTTPError as error:
        if error_handle == "ignore":
            log.message = f"{style} style already exists."
        elif error_handle == "fail":
            raise ValueError(f"{style} style already exists.")
    log.message = f"{style} style created."


@core_exception_logger
def assign_style_to_layer(
    style: str,
    layer: str,
    log: Union[int, Logs] = None,
):
    """TBD"""
    geoserver.assign_style(
        style=style,
        layer=layer,
    )
    log.message = f"{style} style assigned to {layer}."
    postgis.session.commit()


@core_exception_logger
def delete_style_from_server(
    style: str,
    if_used: Literal["fail", "cascade"] = "fail",
    log: Union[int, Logs] = None,
):
    """TBD"""
    geoserver.delete_style(
        style=style,
        purge=True,
        recurse=(if_used == "cascade"),
        if_not_exists="ignore",
    )
    log.message = f"{style} style deleted."
    postgis.session.commit()
