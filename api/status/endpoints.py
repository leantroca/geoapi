from flask_restx import Resource

from utils.geoserver_interface import Geoserver

from . import namespace
from .core import get_log_record

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
        return geoserver.list_layers()


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
        ### parameters:
          - __id__ (requerido): ID del proceso.
        ### responses: 
          - __200__: Registro de estado obtenido correctamente.
          - __500__: Error interno del servidor.
        """
        return get_log_record(id=id)
