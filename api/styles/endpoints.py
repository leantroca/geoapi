from flask_restx import Resource
from api.logger import core_exception_logger, debug_metadata, keep_track

from . import namespace
from .core import (
	push_sld_to_style,
	assign_style_to_layer,
	delete_style_from_server,
)
from .marshal import (
	parse_kwargs,
	upload_sld_parser,
	assign_style_parser,
	delete_style_parser,
)
from utils.postgis_interface import PostGIS


postgis = PostGIS()



class EndpointServer(Resource):
	def logger(self, *args, **kwargs):
		return keep_track(
			endpoint=self.endpoint.replace("_", "/").lower(),
			layer=None,
			status=200,
			message="Received.",
		)


@namespace.route("/sld/form/create")
class SLDFormCreate(EndpointServer):
	"""
	KML File ingest.

	Importa un archivo KML al sistema y genera una nueva capa.
	"""

	@namespace.doc("SLD File import.")
	@namespace.expect(upload_sld_parser, validate=True)
	def post(self):
		"""TBD"""
		# return (log.record, log.status)
		kwargs = parse_kwargs(upload_sld_parser)
		log = self.logger(**kwargs)
		push_sld_to_style(**kwargs, log=log)
		postgis.session.commit()
		return (log.record, log.status)


# @namespace.route("/sld/form/assign")
# class SLDFormCreate(Resource):
# 	"""
# 	KML File ingest.

# 	Importa un archivo KML al sistema y genera una nueva capa.
# 	"""

# 	@namespace.doc("SLD File assign to layer.")
# 	# @namespace.expect(upload_kml_parser, validate=True)
# 	def post(self):
# 		"""TBD"""
# 		# return (log.record, log.status)
# 		return (
# 			{"create": True},
# 			200
# 		)
