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
    kml_to_geometries_parser,
#     delete_layer_parser,
#     download_kml_parser,
    parse_kwargs,
#     upload_kml_parser,
)
from .tasks import (
    task_kml_to_create_batch
#     task_delete_layer,
#     task_kml_to_append_layer,
#     task_kml_to_create_layer,
)


class EndpointServer(Resource):
    def logger(self, *args, **kwargs):

        return keep_track(
            endpoint=self.endpoint.replace("_", "/").lower(),
            layer=None,
            status=200,
            message="Received.",
            json={key: value for key, value in kwargs.items() if is_jsonable(value)},
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
