from models.tables import Logs
from utils.postgis_interface import PostGIS

# from api import postgis

postgis = PostGIS()


def get_log_record(id: int):
    """
    Obtiene el registro de estado de un proceso por su ID.

    Args:
        id (int): ID del proceso.

    Returns:
        dict: Registro de estado del proceso.

    Raises:
        Exception: Error al obtener el registro de estado.
    """
    return postgis.get_log_record(id=id)


def standard_response(**kwargs):
    log = Logs()
    log.update(**kwargs)
    return log.record


def get_batch_record(id: int):
    """
    Obtiene el registro de estado de un proceso por su ID.

    Args:
        id (int): ID del proceso.

    Returns:
        dict: Registro de estado del proceso.

    Raises:
        Exception: Error al obtener el registro de estado.
    """
    return postgis.get_batch_record(id=id)
