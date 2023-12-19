from api.celery import app
from api.logger import get_log, keep_track
from api.utils import temp_remove

from .core import kml_to_append_layer  # get_log,; temp_remove,
from .core import delete_layer, kml_to_create_layer


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_kml_to_create_layer(*args, **kwargs):
    """
    Tarea asincrónica para convertir KML y crear una capa.

    Esta tarea convierte archivos KML en una capa y realiza el proceso de creación de
    capas correspondiente. Luego, elimina el archivo temporal y actualiza el estado
    del registro de registro. Si el estado del registro está en 205 (procesamiento),
    lo actualiza a 210 (éxito) una vez que se completa la tarea.

    Args:
        *args: Argumentos posicionales no especificados.
        **kwargs: Argumentos clave que deben incluir "log", "file" y otros necesarios
            para la función kml_to_create_layer.

    Returns:
        None
    """
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    kml_to_create_layer(*args, **kwargs)
    temp_remove(kwargs["file"])
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_kml_to_append_layer(*args, **kwargs):
    """
    Tarea asincrónica para convertir KML y agregar a capa existente.

    Esta tarea convierte archivos KML y agrega los datos a una capa existente
    correspondiente. Luego, elimina el archivo temporal y actualiza el estado
    del registro de registro. Si el estado del registro está en 205 (procesamiento),
    lo actualiza a 210 (éxito) una vez que se completa la tarea.

    Args:
        *args: Argumentos posicionales no especificados.
        **kwargs: Argumentos clave que deben incluir "log", "file" y otros necesarios
            para la función kml_to_append_layer.

    Returns:
        None
    """
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    kml_to_append_layer(*args, **kwargs)
    temp_remove(kwargs["file"])
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True, max_retries=3, retry_backoff=1)
def task_delete_layer(*args, **kwargs):
    """
    Tarea asincrónica para eliminar una capa.

    Esta tarea elimina una capa y realiza el proceso de eliminación correspondiente.
    Luego, actualiza el estado del registro de registro. Si el estado del registro
    está en 205 (procesamiento), lo actualiza a 210 (éxito) una vez que se completa
    la tarea.

    Args:
        *args: Argumentos posicionales no especificados.
        **kwargs: Argumentos clave que deben incluir "log" y otros necesarios para
            la función delete_layer.

    Returns:
        None
    """
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    delete_layer(*args, **kwargs)
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)
