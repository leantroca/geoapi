from flask_restx import Resource

from . import namespace
from .core import delete_layer, keep_track, kml_to_append_layer, kml_to_create_layer
from .marshal import (
    delete_layer_parser,
    download_kml_parser,
    parse_kwargs,
    upload_kml_parser,
)


@namespace.route("/kml/form/create")
class KMLFormCreate(Resource):
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
        parameters:
          - file (requerido)
          - layer (requerido)
          - obra
          - operatoria
          - provincia
          - departamento
          - municipio
          - localidad
          - estado
          - descripcion
          - cantidad
          - categoria
          - ente
          - fuente
          - metadata
          - error_handle
        responses:
          200:
            Importación exitosa. (OK)
          400:
            Datos de solicitud inválidos. (Solicitud incorrecta)
          500:
            Error interno del servidor. (Error del servidor interno)
        """        
        kwargs = parse_kwargs(upload_kml_parser)
        log = keep_track(
            endpoint="/geoserver/kml/form/create",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_create_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/kml/form/append")
class KMLFormAppend(Resource):
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
        parameters:
          - file (requerido): El archivo KML a importar.
          - layer (requerido): El nombre de la capa de destino donde se agregará el archivo KML.
          - obra: Descripción de la obra.
          - operatoria: Descripción de la operatoria.
          - provincia: Nombre de la provincia.
          - departamento: Nombre del departamento.
          - municipio: Nombre del municipio.
          - localidad: Nombre de la localidad.
          - estado: Estado.
          - descripcion: Descripción.
          - cantidad: Cantidad.
          - categoria: Categoría.
          - ente: Ente.
          - fuente: Fuente.
          - metadata: Metadatos.
          - error_handle: Manejo de errores (opciones: "fail", "replace", "drop").
        responses:
          200:
            Importación exitosa.
          400:
            Datos de solicitud inválidos.
          500:
            Error interno del servidor.
        """
        kwargs = parse_kwargs(upload_kml_parser)
        log = keep_track(
            endpoint="/geoserver/kml/form/append",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_append_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/url/form/create")
class URLFormCreate(Resource):
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
        parameters:
          - url (requerido): La URL o URLs separadas por comas de los archivos KML a importar.
          - layer (requerido): El nombre de la capa de destino donde se creará la capa.
          - obra: Descripción de la obra.
          - operatoria: Descripción de la operatoria.
          - provincia: Nombre de la provincia.
          - departamento: Nombre del departamento.
          - municipio: Nombre del municipio.
          - localidad: Nombre de la localidad.
          - estado: Estado.
          - descripcion: Descripción.
          - cantidad: Cantidad.
          - categoria: Categoría.
          - ente: Ente.
          - fuente: Fuente.
          - metadata: Metadatos.
          - error_handle: Manejo de errores (opciones: "fail", "replace", "drop").
        responses:
          200:
            Importación exitosa.
          400:
            Datos de solicitud inválidos.
          500:
            Error interno del servidor.
        """
        kwargs = parse_kwargs(download_kml_parser)
        log = keep_track(
            endpoint="/geoserver/url/form/create",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_create_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/url/form/append")
class URLFormAppend(Resource):
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
        parameters:
          - url (requerido): La URL o URLs separadas por comas de los archivos KML a agregar.
          - layer (requerido): El nombre de la capa de destino donde se agregarán los datos.
          - obra: Descripción de la obra.
          - operatoria: Descripción de la operatoria.
          - provincia: Nombre de la provincia.
          - departamento: Nombre del departamento.
          - municipio: Nombre del municipio.
          - localidad: Nombre de la localidad.
          - estado: Estado.
          - descripcion: Descripción.
          - cantidad: Cantidad.
          - categoria: Categoría.
          - ente: Ente.
          - fuente: Fuente.
          - metadata: Metadatos.
          - error_handle: Manejo de errores (opciones: "fail", "replace", "drop").
        responses:
          200:
            Agregado exitoso.
          400:
            Datos de solicitud inválidos.
          500:
            Error interno del servidor.
        """
        kwargs = parse_kwargs(download_kml_parser)
        log = keep_track(
            endpoint="/geoserver/kml/form/append",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        kml_to_append_layer(**kwargs, log=log)
        return (log.record, log.status)


@namespace.route("/layer/form/delete")
class DeleteLayer(Resource):
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
        parameters:
          - layer (requerido): El nombre de la capa a eliminar.
          - delete_geometries: Indica si se deben eliminar también las geometrías asociadas (opciones: True, False).
          - metadata: Metadatos de la capa.
          - error_handle: Manejo de errores (opciones: "fail", "ignore").
        responses:
          200:
            Capa eliminada exitosamente.
          400:
            Datos de solicitud inválidos.
          500:
            Error interno del servidor.
        """
        kwargs = parse_kwargs(delete_layer_parser)
        log = keep_track(
            endpoint="/geoserver/layer/form/delete",
            layer=kwargs["layer"],
            status=200,
            message="Received.",
        )
        delete_layer(**kwargs, log=log)
        return (log.record, log.status)
