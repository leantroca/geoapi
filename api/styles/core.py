from api.logger import core_exception_logger, debug_metadata, keep_track
from utils.sld_interface import SLD
from utils.geoserver_interface import Geoserver
from typing import Union, Literal

geoserver = Geoserver()


@core_exception_logger
def push_sld_to_style(
    data: Union[str, FileStorage],
    style: str,
    if_exists: Literal["fail", "replace", "ignore"] = "fail",
):
	"""TBD"""
	sld = SLD(data)

	geoserver.push_style(
        style=style,
        data=sld.read(),
        if_exists=if_exists,
	)
