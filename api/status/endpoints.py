from flask_restx import Namespace, Resource

from utils.geoserver_interface import Geoserver

from .core import get_log_record

geo = Geoserver()


namespace = Namespace(
    "Status", description=f"Endpoints para consultar el estado de {geo.hostname}."
)


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
        responses:
          200:
            Listado de capas obtenido correctamente.
          500:
            Error interno del servidor.
        """
        return geo.list_layers()


@namespace.route("/batch/<int:id>")
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
        parameters:
          - id (requerido): ID del proceso.
        responses:
          200:
            Registro de estado obtenido correctamente.
          500:
            Error interno del servidor.
        """
        return get_log_record(id=id)
