import json
import os
from typing import Union, Optional, Tuple

from utils.postgis_interface import PostGIS
from models.tables import Logs
from utils.general import clean_nones
from werkzeug.exceptions import BadRequest, InternalServerError


postgis = PostGIS()

class Logger(PostGIS):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._log = self.get_log(id=kwargs["log_id"]) if isinstance(kwargs.get("log_id"), int) else None
        self.keep_track(*args, **kwargs)


    @property
    def log(self):
        if not self._log:
            self._log = Logs()
            self.session.add(self._log)
            self.session.commit()
        return self._log
    

    def keep_track(self, *args, **kwargs):
        """
        Registra y actualiza información de seguimiento en la base de datos.

        Args:
            log (Logs, optional): Registro existente en la base de datos. Si no se proporciona,
                se creará uno nuevo. Default es None.
            **kwargs: Pares clave-valor que contienen la información a registrar o actualizar.

        Returns:
            Logs: El registro actualizado en la base de datos.

        """
        self.log.update(**kwargs)
        if "message_append" in kwargs:
            self.message_append(append=kwargs["message_append"])
        self.session.commit()


    def message_append(self, append:str):
        """TBD"""
        self.log.message = (
            ". ".join([self.log.message.strip("."), append.strip(".")]) + "."
        ) if self.log.message else append.strip(".") + "."
        self.session.commit()


    def log_response(self) -> Tuple[dict, int]:
        """
        Obtiene una respuesta de log unificada.

        Args:
        - id (Union[int, Logs]): ID del log o un objeto Log.

        Returns:
        - tuple: Una tupla que contiene el registro del log y su estado.

        """
        return self.log.record, self.log.status



def core_exception_logger(target):
    """
    Decorador para manejar excepciones y registrar información en un log.

    Args:
    - target: Función objetivo a decorar.

    Returns:
    - wrapper: Función envoltorio.

    """

    def wrapper(*args, **kwargs):
        logger = kwargs.get("logger")
        try:
            # TODO: kml_to_create_layer() got multiple values for argument 'file'. [Lea]
            result = target(**kwargs)
            return result
        except Exception as error:
            if isinstance(
                error, BadRequest
            ):
                if logger:
                    logger.keep_track(
                        status = 400,
                        message_append = str(error),
                        json = debug_metadata(**kwargs),
                    )
            elif isinstance(
                error, InternalServerError
            ):
                if logger:
                    logger.keep_track(
                        status = 500,
                        message_append = str(error),
                        json = debug_metadata(**kwargs),
                    )
                raise error
            else:  # serverErrorException
                if logger:
                    logger.keep_track(
                        status = 501,
                        message_append = str(error),
                        json = debug_metadata(**kwargs),
                    )
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
