from flask_restx import Resource

from utils.geoserver_interface import Geoserver

from . import namespace
from .core import get_log_record, standard_response, get_batch_record

geoserver = Geoserver()


@namespace.route("/layers")
class ListLayers(Resource):
    """
    Listado de capas en Geoserver.

    Obtiene la lista de capas disponibles en Geoserver.
    """

    @namespace.doc("List Geoserver Layers.")
    def get(self):
        """
        Obtiene la lista de capas disponibles en Geoserver.

        ---
        ### responses:
          - __200__: Registro de estado obtenido correctamente.
          - __500__: Error interno del servidor.
        """
        return {"layers": geoserver.list_layers()}


@namespace.route("/styles")
class ListStyles(Resource):
    """
    Listado de estilos en Geoserver.

    Obtiene la lista de estilos disponibles en Geoserver.
    """

    @namespace.doc("List Geoserver Styles.")
    def get(self):
        """
        Obtiene la lista de estilos disponibles en Geoserver.

        ---
        ### responses:
          - __200__: Registro de estado obtenido correctamente.
          - __500__: Error interno del servidor.
        """
        return {"styles": geoserver.list_styles()}


@namespace.route("/record/<int:id>")
class ProcessStatus(Resource):
    """
    Estado del proceso.

    Obtiene el registro de estado de un proceso por su ID.
    """

    @namespace.doc("Process status.")
    def get(self, id):
        """
        Obtiene el registro de estado de un proceso por su ID.

        ---
        ### parameters:
          - __id__ (requerido): ID del proceso.
        ### responses:
          - __200__: Registro de estado obtenido correctamente.
          - __500__: Error interno del servidor.
        """
        return get_log_record(id=id) or standard_response(
            id=id,
            endpoint=self.endpoint.replace("_", "/").lower(),
            status=400,
            message=f"Record '{id}' doesn't exist.",
        )


@namespace.route("/batch/<int:id>")
class BatchStatus(Resource):
    """
    Estado del batch.

    Obtiene el registro de estado de un batch por su ID.
    """

    @namespace.doc("Batch status.")
    def get(self, id):
        """
        Obtiene el registro de estado de un batch por su ID.

        ---
        ### parameters:
          - __id__ (requerido): ID del batch.
        ### responses:
          - __200__: Registro de batch obtenido correctamente.
          - __500__: Error interno del servidor.
        """
        return get_batch_record(id=id) or standard_response(
            id=id,
            endpoint=self.endpoint.replace("_", "/").lower(),
            status=400,
            message=f"Batch '{id}' doesn't exist.",
        )
