from api.logger import EndpointServer, Logger, debug_metadata
from api.utils import temp_remove, temp_store

from . import namespace
from .core import (  # get_log_response,; temp_remove,; temp_store,
    verify_layer_exists,
    verify_layer_not_exists,
)
from .marshal import (
    delete_layer_parser,
    download_kml_parser,
    parse_kwargs,
    upload_kml_parser,
)
from .tasks import task_delete_layer, task_kml_to_append_layer, task_kml_to_create_layer


@namespace.route("/kml/form/create")
class KMLFormCreate(EndpointServer):
    """
    KML File ingest.

    Importa un archivo KML al sistema y genera una nueva capa.
    """

    @namespace.doc("KML File import.")
    @namespace.expect(upload_kml_parser, validate=True)
    def post(self):
        """
        Importa un archivo KML para crear una capa en GeoServer.

        ---
        ### parameters:
          - __file__ (requerido): El archivo KML a importar.
          - __layer__ (requerido): El nombre de la capa de destino donde se creará la capa.
          - __obra__: Descripción de la obra.
          - __operatoria__: Descripción de la operatoria.
          - __provincia__: Nombre de la provincia.
          - __departamento__: Nombre del departamento.
          - __municipio__: Nombre del municipio.
          - __localidad__: Nombre de la localidad.
          - __estado__: Estado.
          - __descripcion__: Descripción.
          - __cantidad__: Cantidad.
          - __categoria__: Categoría.
          - __ente__: Ente.
          - __fuente__: Fuente.
          - __metadata__: Metadatos.
          - __error_handle__: Manejo de errores (opciones: "fail", "replace", "drop").
        ---
        ### responses:
          - __200__: Importación exitosa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)
        """
        kwargs = parse_kwargs(upload_kml_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                # TODO: Verificar archivo antes de continuar. [Lea]
                kwargs["file"] = temp_store(kwargs["file"])
                verify_layer_not_exists(kwargs["layer"])
                # task.delay requiere argumentos que sean JSON serializable.
                task_kml_to_create_layer.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                # Algo falló con los parámetros.
                # TODO: Unificar con verificación de archivo. [Leo]
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
                temp_remove(kwargs["file"])
            return logger.log_response()


@namespace.route("/kml/form/append")
class KMLFormAppend(EndpointServer):
    """
    KML File append.

    Importa un archivo KML al sistema y lo agrega a una capa existente.
    """

    @namespace.doc("KML File ingest.")
    @namespace.expect(upload_kml_parser, validate=True)
    def put(self):
        """
        Importa un archivo KML al sistema y lo agrega a una capa existente.

        ---
        ### parameters:
          - __file__ (requerido): El archivo KML a importar.
          - __layer__ (requerido): El nombre de la capa de destino donde se agregará el archivo KML.
          - __obra__: Descripción de la obra.
          - __operatoria__: Descripción de la operatoria.
          - __provincia__: Nombre de la provincia.
          - __departamento__: Nombre del departamento.
          - __municipio__: Nombre del municipio.
          - __localidad__: Nombre de la localidad.
          - __estado__: Estado.
          - __descripcion__: Descripción.
          - __cantidad__: Cantidad.
          - __categoria__: Categoría.
          - __ente__: Ente.
          - __fuente__: Fuente.
          - __metadata__: Metadatos.
          - __error_handle__: Manejo de errores (opciones: "fail", "replace", "drop").
        ---
        ### responses:
          - __200__: Importación exitosa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)

        """
        kwargs = parse_kwargs(upload_kml_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                # TODO: Verificar archivo antes de continuar. [Lea]
                kwargs["file"] = temp_store(kwargs["file"])
                verify_layer_exists(kwargs["layer"])
                # task.delay requiere argumentos que sean JSON serializable.
                task_kml_to_append_layer.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                # Algo falló con los parámetros.
                # TODO: Unificar con verificación de archivo. [Leo]
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
                temp_remove(kwargs["file"])
            return logger.log_response()


@namespace.route("/url/form/create")
class URLFormCreate(EndpointServer):
    """
    KML URL ingest.

    Importa archivos KML desde URLs y crea una capa en GeoServer.
    """

    @namespace.doc("KML URL ingest.")
    @namespace.expect(download_kml_parser, validate=True)
    def post(self):
        """
        Importa archivos KML desde URLs y crea una capa en GeoServer.

        ---
        ### parameters:
          - __url__ (requerido): La URL o URLs separadas por comas de los archivos KML a importar.
          - __layer__ (requerido): El nombre de la capa de destino donde se creará la capa.
          - __obra__: Descripción de la obra.
          - __operatoria__: Descripción de la operatoria.
          - __provincia__: Nombre de la provincia.
          - __departamento__: Nombre del departamento.
          - __municipio__: Nombre del municipio.
          - __localidad__: Nombre de la localidad.
          - __estado__: Estado.
          - __descripcion__: Descripción.
          - __cantidad__: Cantidad.
          - __categoria__: Categoría.
          - __ente__: Ente.
          - __fuente__: Fuente.
          - __metadata__: Metadatos.
          - __error_handle__: Manejo de errores (opciones: "fail", "replace", "drop").
        ---
        ### responses:
          - __200__: Importación exitosa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)

        """
        kwargs = parse_kwargs(download_kml_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                # TODO: Verificar archivo antes de continuar. [Lea]
                kwargs["file"] = temp_store(kwargs["file"])
                verify_layer_not_exists(kwargs["layer"])
                task_kml_to_create_layer.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                # Algo falló con los parámetros.
                # TODO: Unificar con verificación de archivo. [Leo]
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
                temp_remove(kwargs["file"])
            return logger.log_response()


@namespace.route("/url/form/append")
class URLFormAppend(EndpointServer):
    """
    KML URL append.

    Agrega archivos KML desde URLs a una capa existente en GeoServer.
    """

    @namespace.doc("KML URL append.")
    @namespace.expect(download_kml_parser, validate=True)
    def put(self):
        """
        Agrega archivos KML desde URLs a una capa existente en GeoServer.

        ---
        ### parameters:
          - __url__ (requerido): La URL o URLs separadas por comas de los archivos KML a agregar.
          - __layer__ (requerido): El nombre de la capa de destino donde se agregarán los datos.
          - __obra__: Descripción de la obra.
          - __operatoria__: Descripción de la operatoria.
          - __provincia__: Nombre de la provincia.
          - __departamento__: Nombre del departamento.
          - __municipio__: Nombre del municipio.
          - __localidad__: Nombre de la localidad.
          - __estado__: Estado.
          - __descripcion__: Descripción.
          - __cantidad__: Cantidad.
          - __categoria__: Categoría.
          - __ente__: Ente.
          - __fuente__: Fuente.
          - __metadata__: Metadatos.
          - __error_handle__: Manejo de errores (opciones: "fail", "replace", "drop").
        ---
        ### responses:
          - __200__: Importación exitosa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)

        """
        kwargs = parse_kwargs(download_kml_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                # TODO: Verificar archivo antes de continuar. [Lea]
                kwargs["file"] = temp_store(kwargs["file"])
                verify_layer_exists(kwargs["layer"])
                task_kml_to_append_layer.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                # Algo falló con los parámetros.
                # TODO: Unificar con verificación de archivo. [Leo]
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
                temp_remove(kwargs["file"])
            return logger.log_response()


@namespace.route("/layer/form/delete")
class DeleteLayer(EndpointServer):
    """
    Eliminación de capa completa.

    Elimina una capa y sus datos asociados en GeoServer.
    """

    @namespace.doc("KML File removal.")
    @namespace.expect(delete_layer_parser, validate=True)
    def delete(self):
        """
        Elimina una capa y sus datos asociados en GeoServer.

        ---
        ### parameters:
          - __layer__ (requerido): El nombre de la capa a eliminar.
          - __delete_geometries__: Indica si se deben eliminar también las geometrías asociadas (opciones: True, False).
          - __metadata__: Metadatos de la capa.
          - __error_handle__: Manejo de errores (opciones: "fail", "ignore").
        ---
        ### responses:
          - __200__: Importación exitosa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)

        """
        # TODO: Esta tarea podría ser sincrónica. [Lea]
        kwargs = parse_kwargs(delete_layer_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            task_delete_layer.delay(**kwargs, log_id=logger.log.id)
            return logger.log_response()
