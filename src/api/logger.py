import os
from typing import Union

from models.tables import Logs
from utils.general import clean_nones
from utils.geoserver_interface import Geoserver
from utils.postgis_interface import PostGIS

postgis = PostGIS()
geoserver = Geoserver()


def core_exception_logger(target):
    def wrapper(*args, **kwargs):
        log = kwargs.get("log") or keep_track()
        if isinstance(log, int):
            log = postgis.get_log(id=log)
        kwargs["log"] = log
        try:
            result = target(**kwargs)
            postgis.session.commit()
            return result
        except Exception as error:
            if isinstance(
                error, ValueError
            ):  # reemplazar los: ValueError por: badRequestException
                log.status = 400
                log.message = str(error)
                log.json = debug_metadata(**kwargs)
                postgis.session.commit()
            else:  # serverErrorException
                log.status = 500
                log.message = str(error)
                log.json = debug_metadata(**kwargs)
                postgis.session.commit()
                raise error

    return wrapper


def debug_metadata(**kwargs) -> dict:
    return clean_nones(
        {
            key: value
            if key not in ["file"]
            else str([os.path.basename(element) for element in value])
            for key, value in kwargs.items()
            if key not in ["log"]
        }
    )


def keep_track(log: Union[int, Logs] = None, **kwargs):
    """
    Registra y actualiza información de seguimiento en la base de datos.

    Args:
        log (Logs, optional): Registro existente en la base de datos. Si no se proporciona,
            se creará uno nuevo. Default es None.
        **kwargs: Pares clave-valor que contienen la información a registrar o actualizar.

    Returns:
        Logs: El registro actualizado en la base de datos.

    """
    if log is None:
        log = Logs()
        postgis.session.add(log)
    if isinstance(log, int):
        log = postgis.get_log(id=log)
    postgis.session.flush()
    log.update(**kwargs)
    postgis.session.commit()
    return log
