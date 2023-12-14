from flask_restx import Resource

from api.logger import debug_metadata, keep_track, get_log_response, is_jsonable
from api.utils import temp_store, temp_remove

from . import namespace
# from .core import (
#     get_log_response,
#     temp_remove,
#     temp_store,
#     verify_layer_exists,
#     verify_layer_not_exists,
# )
from .marshal import (
    parse_kwargs,
    parse_ids,
    kml_to_geometries_parser,
    url_to_geometries_parser,
    view_to_push_parser,
    delete_geometry_parser,
    delete_batch_parser,
)
from .tasks import (
    task_kml_to_create_batch,
    task_view_push_to_layer,
    task_delete_geometries,
    task_delete_batches,
)


class EndpointServer(Resource):
    def logger(self, *args, **kwargs):

        return keep_track(
            endpoint=self.endpoint.replace("_", "/").lower(),
            layer=None,
            status=200,
            message="Received.",
            json={key: value for key, value in kwargs.items() if key != "file"},
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
        log_id = self.logger(**kwargs).id
        try:
            kwargs["file"] = temp_store(kwargs["file"])
            # log_id = log if isinstance(log, int) else log.id
            task_kml_to_create_batch.delay(**kwargs, log=log_id)
        except ValueError as error:
            keep_track(
                log=log_id,
                status=400,
                message=str(error),
                json=debug_metadata(**kwargs),
            )
            temp_remove(kwargs["file"])
        return get_log_response(log_id)



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
        log_id = self.logger(**kwargs).id
        try:
            kwargs["file"] = temp_store(kwargs["file"])
            # log_id = log if isinstance(log, int) else log.id
            task_kml_to_create_batch.delay(**kwargs, log=log_id)
        except ValueError as error:
            keep_track(
                log=log_id,
                status=400,
                message=str(error),
                json=debug_metadata(**kwargs),
            )
            temp_remove(kwargs["file"])
        return get_log_response(log_id)


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
        log_id = self.logger(**kwargs).id
        try:
            task_view_push_to_layer.delay(**kwargs, log=log_id)
        except ValueError as error:
            keep_track(
                log=log_id,
                status=400,
                message=str(error),
                json=debug_metadata(**kwargs),
            )
        return get_log_response(log_id)



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
        log_id = self.logger(**kwargs).id
        task_delete_geometries.delay(**kwargs, log=log_id)
        return get_log_response(log_id)


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
        log_id = self.logger(**kwargs).id
        task_delete_batches.delay(**kwargs, log=log_id)
        return get_log_response(log_id)
