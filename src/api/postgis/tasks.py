from api.celery import app
from api.logger import keep_track, get_log, get_log_response

from api.utils import temp_remove

from .core import (
    kml_to_create_batch,
    view_push_to_layer,
    delete_geometries,
    delete_batches,
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
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    kml_to_create_batch(*args, **kwargs)
    temp_remove(kwargs["file"])
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_view_push_to_layer(*args, **kwargs):
    """
    Realiza la tarea de crear una capa en Geoserver y actualiza el log.

    Args:
    - args: Argumentos posicionales.
    - kwargs: Argumentos clave-valor.

    """
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    view_push_to_layer(*args, **kwargs)
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_delete_geometries(*args, **kwargs):
    """
    Realiza la tarea de eliminar geometrías y actualiza el log.

    Args:
    - args: Argumentos posicionales.
    - kwargs: Argumentos clave-valor.

    """
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    delete_geometries(**kwargs)
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_delete_batches(*args, **kwargs):
    """
    Realiza la tarea de eliminar lotes y actualiza el log.

    Args:
    - args: Argumentos posicionales.
    - kwargs: Argumentos clave-valor.

    """
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    delete_batches(**kwargs)
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)
