from typing import Literal, Optional, Union

from requests.exceptions import HTTPError
from werkzeug.datastructures import FileStorage

from api.logger import Logger, core_exception_logger
from utils.geoserver_interface import Geoserver
from utils.sld_interface import SLD

geoserver = Geoserver()


def list_available_layers():
    """
    Lista las capas disponibles.

    Esta función devuelve una lista de estilos disponibles en el servidor Geoserver.

    Returns:
        List[str]: Una lista de nombres de estilos disponibles.
    """
    return geoserver.list_styles()


@core_exception_logger
def push_sld_to_style(
    file: Union[str, FileStorage],
    style: str,
    error_handle: Literal["fail", "replace", "ignore"] = "fail",
    logger: Optional[Logger] = None,
    **kwargs,
):
    """
    Carga una definición de estilo SLD en un estilo en el servidor Geoserver.

    Esta función toma un archivo SLD o contenido de SLD, carga la definición en el
    estilo especificado en el servidor Geoserver y maneja errores según las opciones
    proporcionadas. Actualiza el registro de registro con los mensajes apropiados.

    Args:
        file (Union[str, FileStorage]): Ruta de archivo o objeto FileStorage que
            contiene la definición de estilo SLD.
        style (str): Nombre del estilo en el que se cargará la definición.
        error_handle (Literal["fail", "replace", "ignore"], optional): Controla el
            comportamiento en caso de un estilo existente. Opciones: "fail" (por defecto)
            para lanzar un error, "replace" para reemplazar el estilo, "ignore" para
            ignorar el error.
        log (Union[int, Logs], optional): Un ID de registro o objeto Logs para
            actualizar el registro de registro. Por defecto es None.

    Returns:
        None
    """
    sld = SLD(file)
    try:
        geoserver.push_style(
            style=style,
            data=sld.read(),
            if_exists=error_handle,
        )
    except HTTPError:
        if error_handle == "ignore":
            return
        elif error_handle == "fail":
            raise
    if logger:
        logger.keep_track(message_append=f"{style} style created.")


@core_exception_logger
def assign_style_to_layer(
    style: str,
    layer: str,
    error_handle: Literal["fail", "ignore"] = "fail",
    logger: Optional[Logger] = None,
    **kwargs,
):
    """
    Asigna un estilo a una capa en el servidor Geoserver.

    Esta función toma un nombre de estilo y un nombre de capa, y asigna el estilo a la
    capa correspondiente en el servidor Geoserver. Actualiza el registro de registro con
    los mensajes apropiados.

    Args:
        style (str): Nombre del estilo que se asignará a la capa.
        layer (str): Nombre de la capa a la que se asignará el estilo.
        log (Union[int, Logs], optional): Un ID de registro o objeto Logs para
            actualizar el registro de registro. Por defecto es None.

    Returns:
        None
    """
    try:
        geoserver.assign_style(
            style=style,
            layer=layer,
        )
    except HTTPError:
        if error_handle == "ignore":
            return
        elif error_handle == "fail":
            raise
    if logger:
        logger.keep_track(message_append=f"{style} style assigned to {layer}.")


@core_exception_logger
def delete_style_from_server(
    style: str,
    error_handle: Literal["fail", "cascade"] = "fail",
    logger: Optional[Logger] = None,
    **kwargs,
):
    """
    Elimina un estilo del servidor Geoserver.

    Esta función elimina un estilo del servidor Geoserver y maneja errores según las
    opciones proporcionadas. Actualiza el registro de registro con los mensajes
    apropiados.

    Args:
        style (str): Nombre del estilo que se eliminará.
        error_handle (Literal["fail", "cascade"], optional): Controla el comportamiento
            en caso de que el estilo no exista. Opciones: "fail" (por defecto) para
            lanzar un error, "cascade" para eliminar el estilo y sus capas asociadas.
        log (Union[int, Logs], optional): Un ID de registro o objeto Logs para
            actualizar el registro de registro. Por defecto es None.

    Returns:
        None
    """
    try:
        geoserver.delete_style(
            style=style,
            purge=True,
            recurse=(error_handle == "cascade"),
            if_not_exists="ignore",
        )
    except HTTPError:
        if error_handle == "ignore":
            return
        elif error_handle == "fail":
            raise
    if logger:
        logger.keep_track(message_append=f"{style} style deleted.")
