from api.celery import app
from api.logger import get_log, keep_track, Logger
from api.utils import temp_remove

from .core import (
    delete_batches,
    delete_geometries,
    kml_to_create_batch,
    view_push_to_layer,
)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_kml_to_create_batch(*args, **kwargs):
    """
    Tarea asincrónica para convertir KML y crear un batch.

    Esta tarea convierte archivos KML en un batch. Luego, elimina el archivo temporal
    y actualiza el estado del registro de registro. Si el estado del registro está en
    205 (procesamiento), lo actualiza a 210 (éxito) una vez que se completa la tarea.

    Args:
        *args: Argumentos posicionales no especificados.
        **kwargs: Argumentos clave que deben incluir "log", "file" y otros necesarios
            para la función kml_to_create_layer.

    Returns:
        None
    """
    with Logger(log_id=kwargs["log_id"]) as logger:
        logger.keep_track(message="Processing.", status=205)
        kml_to_create_batch(*args, **kwargs, logger=logger)
        temp_remove(kwargs["file"])
        if logger.log.status == 205:
            logger.keep_track(message_append="Success", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_view_push_to_layer(*args, **kwargs):
    """
    Realiza la tarea de crear una capa en Geoserver y actualiza el log.

    Args:
    - args: Argumentos posicionales.
    - kwargs: Argumentos clave-valor.

    """
    with Logger(log_id=kwargs["log_id"]) as logger:
        logger.keep_track(message="Processing.", status=205)
        view_push_to_layer(*args, **kwargs, logger=logger)
        if logger.log.status == 205:
            logger.keep_track(message_append="Success", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_delete_geometries(*args, **kwargs):
    """
    Realiza la tarea de eliminar geometrías y actualiza el log.

    Args:
    - args: Argumentos posicionales.
    - kwargs: Argumentos clave-valor.

    """
    with Logger(log_id=kwargs["log_id"]) as logger:
        logger.keep_track(message="Processing.", status=205)
        delete_geometries(**kwargs, logger=logger)
        if logger.log.status == 205:
            logger.keep_track(message_append="Success", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_delete_batches(*args, **kwargs):
    """
    Realiza la tarea de eliminar lotes y actualiza el log.

    Args:
    - args: Argumentos posicionales.
    - kwargs: Argumentos clave-valor.

    """
    with Logger(log_id=kwargs["log_id"]) as logger:
        logger.keep_track(message="Processing.", status=205)
        delete_batches(**kwargs, logger=logger)
        if logger.log.status == 205:
            logger.keep_track(message_append="Success", status=210)
