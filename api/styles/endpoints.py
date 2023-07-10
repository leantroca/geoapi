from flask_restx import Resource

from . import namespace



class EndpointServer(Resource):
	def logger(self, *args, **kwargs):
		return keep_track(
			endpoint=self.endpoint.replace("_", "/").lower(),
			layer=kwargs["layer"],
			status=200,
			message="Received.",
		)


@namespace.route("/sld/form/create")
class SLDFormCreate(Resource):
	"""
	KML File ingest.

	Importa un archivo KML al sistema y genera una nueva capa.
	"""

	@namespace.doc("SLD File import.")
	# @namespace.expect(upload_kml_parser, validate=True)
	def post(self):
		"""TBD"""
		# return (log.record, log.status)
		return (
			{"create": True},
			200
		)


@namespace.route("/sld/form/assign")
class SLDFormCreate(Resource):
	"""
	KML File ingest.

	Importa un archivo KML al sistema y genera una nueva capa.
	"""

	@namespace.doc("SLD File assign to layer.")
	# @namespace.expect(upload_kml_parser, validate=True)
	def post(self):
		"""TBD"""
		# return (log.record, log.status)
		return (
			{"create": True},
			200
		)