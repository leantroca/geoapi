from requests.exceptions import HTTPError

from api.logger import EndpointServer, Logger, debug_metadata

from . import namespace
from .core import assign_style_to_layer, delete_style_from_server, push_sld_to_style
from .marshal import (
    assign_style_parser,
    delete_style_parser,
    parse_kwargs,
    upload_style_parser,
)


@namespace.route("/create/form")
class StyleCreateForm(EndpointServer):
    """
    Clase de ruta para el formulario de creación de estilos.

    Esta clase define una ruta para importar un archivo SLD y crear un estilo en el
    servidor. Utiliza el analizador upload_style_parser para recibir los datos del
    formulario y llama a la función push_sld_to_style para procesar la solicitud.

    """

    @namespace.doc("SLD File import.")
    @namespace.expect(upload_style_parser, validate=True)
    def post(self):
        """
        Maneja las solicitudes POST para importar archivos SLD y crear estilos.

        ---
        ### Parámetros:
          - __file__ (requerido): El archivo SLD a importar.
          - __style__ (requerido): El nombre del estilo que se creará.
          - __error_handle__: Manejo de errores (opciones: "fail", "replace", "ignore").
                - __fail__: Falla si el estilo ya existe.
                - __replace__: Reemplaza cualquier estilo previo con el mismo nombre.
                - __ignore__: Evita crear un nuevo estilo si ya existe uno previo con el mismo nombre.

        ### Respuestas:
          - __200__: Creación exitosa del estilo. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)
        """
        kwargs = parse_kwargs(upload_style_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                push_sld_to_style(**kwargs, logger=logger)
            except HTTPError as error:
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
            return logger.log_response()


@namespace.route("/assign/form")
class StyleAssignForm(EndpointServer):
    """
    Clase de ruta para el formulario de asignación de estilos.

    Esta clase define una ruta para asignar un estilo a una capa en el servidor. Utiliza
    el analizador assign_style_parser para recibir los datos del formulario y llama a la
    función assign_style_to_layer para procesar la solicitud.

    """

    @namespace.doc("Assign style to layer.")
    @namespace.expect(assign_style_parser, validate=True)
    def put(self):
        """
        Maneja las solicitudes PUT para asignar estilos a capas.

        ---
        ### Parámetros:
          - __style__ (requerido): El nombre del estilo que se asignará a la capa.
          - __layer__ (requerido): El nombre de la capa a la que se asignará el estilo.
          - __error_handle__: Manejo de errores (opciones: "fail", "ignore").
                - __fail__: Previene eliminar un estilo que esté en uso por una capa.
                - __ignore__: Evita asignar un nuevo estilo si no existe uno previo con el mismo nombre.

        ### Respuestas:
          - __200__: Asignación exitosa del estilo a la capa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)
        """
        kwargs = parse_kwargs(assign_style_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                assign_style_to_layer(**kwargs, logger=logger)
            except HTTPError as error:
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
            return logger.log_response()


@namespace.route("/delete/form")
class StyleDeleteForm(EndpointServer):
    """
    Clase de ruta para el formulario de eliminación de estilos.

    Esta clase define una ruta para eliminar un estilo del servidor.

    """

    @namespace.doc("Delete style from server.")
    @namespace.expect(delete_style_parser, validate=True)
    def delete(self):
        """
        Maneja las solicitudes DELETE para eliminar estilos del servidor.

        ---
        ### Parámetros:
          - __style__ (requerido): El nombre del estilo que se eliminará.
          - __error_handle__: Manejo de errores (opciones: "fail", "cascade").
                - __fail__: Previene eliminar un estilo que esté en uso por una capa.
                - __cascade__: Fuerza la eliminación del estilo y asigna el estilo por
                        defecto a cualquier capa usándo el estilo eliminado.
        ### Respuestas:
          - __200__: Eliminación exitosa del estilo. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)
        """
        kwargs = parse_kwargs(delete_style_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                delete_style_from_server(**kwargs, logger=logger)
            except HTTPError as error:
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
            return logger.log_response()
