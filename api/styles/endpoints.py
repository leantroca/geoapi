from flask_restx import Resource
from api.logger import core_exception_logger, debug_metadata, keep_track

from . import namespace
from .core import (
	list_available_layers,
	push_sld_to_style,
	assign_style_to_layer,
	delete_style_from_server,
)
from .marshal import (
	parse_kwargs,
	upload_style_parser,
	assign_style_parser,
	delete_style_parser,
)
from utils.postgis_interface import PostGIS
from requests.exceptions import HTTPError


postgis = PostGIS()



class EndpointServer(Resource):
	def logger(self, *args, **kwargs):
		return keep_track(
			endpoint=self.endpoint.replace("_", "/").lower(),
			layer=None,
			status=200,
			message="Received.",
		)


@namespace.route("/list")
class StyleList(Resource):
	"""TBD	"""

	@namespace.doc("List available styles.")
	def get(self):
		"""TBD"""
		return list_available_layers()


@namespace.route("/create/form")
class StyleCreateForm(EndpointServer):
	"""
	KML File ingest.

	Importa un archivo KML al sistema y genera una nueva capa.
	"""

	@namespace.doc("SLD File import.")
	@namespace.expect(upload_style_parser, validate=True)
	def post(self):
		"""TBD"""
		kwargs = parse_kwargs(upload_style_parser)
		log = self.logger(**kwargs)
		push_sld_to_style(**kwargs, log=log)
		return (log.record, log.status)


@namespace.route("/assign/form")
class StyleAssignForm(EndpointServer):
	"""TBD"""

	@namespace.doc("Assign style to layer.")
	@namespace.expect(assign_style_parser, validate=True)
	def put(self):
		"""TBD"""
		kwargs = parse_kwargs(assign_style_parser)
		log = self.logger(**kwargs)
		assign_style_to_layer(**kwargs, log=log)
		return (log.record, log.status)


@namespace.route("/delete/form")
class StyleDeleteForm(EndpointServer):
	"""TBD"""

	@namespace.doc("Delete style from server.")
	@namespace.expect(delete_style_parser, validate=True)
	def delete(self):
		"""TBD"""
		kwargs = parse_kwargs(delete_style_parser)
		log = self.logger(**kwargs)
		try:
			delete_style_from_server(**kwargs, log=log)
		except HTTPError as error:
			keep_track(log, status=400, message=str(error))
		return (log.record, log.status)
