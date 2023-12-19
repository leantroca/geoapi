import json
import os
from typing import Union

from api.celery import postgis
from models.tables import Logs
from utils.general import clean_nones


def core_exception_logger(target):
    """
    Decorador para manejar excepciones y registrar información en un log.

    Args:
    - target: Función objetivo a decorar.

    Returns:
    - wrapper: Función envoltorio.

    """

    def wrapper(*args, **kwargs):
        log_id = kwargs.get("log") or keep_track()
        log_id = log_id.id if isinstance(log_id, Logs) else log_id
        # if isinstance(log_id, int):
        #     log = postgis.get_log(id=log)
        kwargs["log"] = log_id
        try:
            result = target(**kwargs)
            postgis.session.commit()
            return result
        except Exception as error:
            log = postgis.get_log(id=log_id)
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
    """
    Genera metadatos para depuración, eliminando valores 'None' y obteniendo nombres base de archivos.

    Args:
    - kwargs: Argumentos de la función.

    Returns:
    - dict: Metadatos depurados.

    """
    return clean_nones(
        {
            key: value
            if key not in ["file"]
            else str([os.path.basename(element) for element in value])
            for key, value in kwargs.items()
            if key not in ["log"]
        }
    )


def keep_track(log: Union[int, Logs] = None, **kwargs) -> Logs:
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


def get_log(id: Union[int, Logs]):
    """
    Recupera un registro de registro o una lista de registros según el ID proporcionado.

    Esta función toma un ID de registro único o un objeto Logs y recupera el registro
    correspondiente utilizando el módulo postgis.get_log si se proporciona un ID entero,
    o simplemente devuelve el objeto Logs si ya es proporcionado.

    Args:
        id (Union[int, Logs]): Un ID de registro único o un objeto Logs que se utilizará
            para recuperar el registro o se devolverá directamente.

    Returns:
        El registro de registro correspondiente si se proporciona un ID entero, o el
        objeto Logs proporcionado.

    Notas:
        - Si se proporciona un objeto Logs en lugar de un ID, se devolverá ese objeto
          sin realizar ninguna operación adicional.
        - Si se proporciona un ID entero, se utilizará el módulo postgis.get_log para
          recuperar el registro de registro correspondiente.

    """
    return postgis.get_log(id=id) if isinstance(id, int) else id


def get_log_response(id: Union[int, Logs]):
    """
    Obtiene una respuesta de log unificada.

    Args:
    - id (Union[int, Logs]): ID del log o un objeto Log.

    Returns:
    - tuple: Una tupla que contiene el registro del log y su estado.

    """
    log = get_log(id=id)
    return log.record, log.status


def is_jsonable(obj):
    """
    Verifica si un objeto es serializable a JSON.

    Args:
    - obj: El objeto a verificar.

    Returns:
    - bool: True si el objeto es serializable a JSON, False en caso contrario.

    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
