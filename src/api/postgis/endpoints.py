from api.logger import EndpointServer, Logger, debug_metadata
from api.utils import temp_remove, temp_store

from . import namespace
from .marshal import (
    delete_batch_parser,
    delete_geometry_parser,
    kml_to_geometries_parser,
    parse_ids,
    parse_kwargs,
    url_to_geometries_parser,
    view_to_push_parser,
)
from .tasks import (
    task_delete_batches,
    task_delete_geometries,
    task_kml_to_create_batch,
    task_view_push_to_layer,
)


@namespace.route("/kml/form/ingest")
class KMLFormIngest(EndpointServer):
    """
    KML File ingest.

    Importa geometrías de un archivo KML a la base de datos PostGIS.
    """

    @namespace.doc("KML File ingest.")
    @namespace.expect(kml_to_geometries_parser, validate=True)
    def post(self):
        """
        Importa un archivo KML para crear geometrías en PostGIS.

        ---
        ### parameters:
          - __file__ (requerido): El archivo KML a importar.
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
        kwargs = parse_kwargs(kml_to_geometries_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                kwargs["file"] = temp_store(kwargs["file"])
                task_kml_to_create_batch.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                # TODO: Este except se repite igual en todos los endpoints. Unificar. [Lea]
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
                temp_remove(kwargs["file"])
            return logger.log_response()


@namespace.route("/url/form/ingest")
class URLFormCreate(EndpointServer):
    """
    KML URL ingest.

    Importa geometrías desde una URL a la base de datos PostGIS.
    """

    @namespace.doc("KML URL ingest.")
    @namespace.expect(url_to_geometries_parser, validate=True)
    def post(self):
        """
        Importa archivos KML desde URLs para crear geometrías en PostGIS.

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
        kwargs = parse_kwargs(url_to_geometries_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                kwargs["file"] = temp_store(kwargs["file"])
                task_kml_to_create_batch.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
                temp_remove(kwargs["file"])
            return logger.log_response()


@namespace.route("/layer/form/push")
class ViewFormPush(EndpointServer):
    """
    Postgis View Push.

    Crea una capa en Geoserver a partir de una Vista preexistente en PostGIS.
    """

    @namespace.doc("PostGIS Layer push.")
    @namespace.expect(view_to_push_parser, validate=True)
    def post(self):
        """
        Crea una capa en Geoserver a partir de una Vista preexistente en PostGIS
        ---
        ### parameters:
          - __layer__ (requerido): El nombre de la capa de destino donde se creará la capa.
          - __metadata__: Metadatos.
          - __error_handle__: Manejo de errores (opciones: "fail", "drop").
        ---
        ### responses:
          - __200__: Creación de capa exitosa. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)
        """
        kwargs = parse_kwargs(view_to_push_parser)
        with Logger(**self.job_received(**kwargs)) as logger:
            try:
                task_view_push_to_layer.delay(**kwargs, log_id=logger.log.id)
            except ValueError as error:
                logger.keep_track(
                    status=400,
                    message=str(error),
                    json=debug_metadata(**kwargs),
                )
            return logger.log_response()


@namespace.route("/delete/geometry")
class DeleteGeometry(EndpointServer):
    """
    Elimina una o varias geometrías por id.
    """

    @namespace.doc("Geometry deletion.")
    @namespace.expect(delete_geometry_parser, validate=True)
    def delete(self):
        """
        Elimina geometrías en PostGIS.

        ---
        ### parameters:
          - __geometry_id__ (requerido): El id de la geometría a eliminar.
          - __metadata__: Metadatos de la capa.
          - __error_handle__: Manejo de errores (opciones: "fail", "ignore").
        ---
        ### responses:
          - __200__: Proceso exitoso. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)

        """
        kwargs = parse_kwargs(delete_geometry_parser)
        kwargs = parse_ids(kwargs)
        with Logger(**self.job_received(**kwargs)) as logger:
            task_delete_geometries.delay(**kwargs, log_id=logger.log.id)
            return logger.log_response()


@namespace.route("/delete/batch")
class DeleteBatch(EndpointServer):
    """
    Elimina uno o varios batches por id.
    """

    @namespace.doc("Batch deletion.")
    @namespace.expect(delete_batch_parser, validate=True)
    def delete(self):
        """
        Elimina batches en PostGIS.

        ---
        ### parameters:
          - __batch_id__ (requerido): El id del batch eliminar.
          - __metadata__: Metadatos de la capa.
          - __error_handle__: Manejo de errores (opciones: "fail", "ignore").
        ---
        ### responses:
          - __200__: Proceso exitoso. (OK)
          - __400__: Datos de solicitud inválidos. (Solicitud incorrecta)
          - __500__: Error interno del servidor. (Error del servidor interno)
        """
        kwargs = parse_kwargs(delete_batch_parser)
        kwargs = parse_ids(kwargs)
        with Logger(**self.job_received(**kwargs)) as logger:
            task_delete_batches.delay(**kwargs, log_id=logger.log.id)
            return logger.log_response()
