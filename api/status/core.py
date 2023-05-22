from utils.postgis_interface import PostGIS

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
