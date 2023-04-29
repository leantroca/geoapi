from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

# # Look only in the POST body
# parser.add_argument('name', type=int, location='form')
#
# # Look only in the querystring
# parser.add_argument('PageSize', type=int, location='args')
#
# # From the request headers
# parser.add_argument('User-Agent', location='headers')
#
# # From http cookies
# parser.add_argument('session_id', location='cookies')
#
# # From file uploads
# parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')
#
# Docs on argument construction in:
# https://flask-restx.readthedocs.io/en/latest/api.html#module-flask_restx.reqparse

file = reqparse.Argument(
    "KML File",
    dest="file",
    location="files",
    type=FileStorage,
    required=True,
    help="KML file to be imported.",
)

layer = reqparse.Argument(
    "Target Layer Name",
    dest="layer",
    location="form",
    type=str,
    required=True,
    help="Target layer name to be created.",
)

username = reqparse.Argument(
    "Geoserver Username",
    dest="user",
    location="form",
    type=str,
    required=True,
    help="Your username for wms.minhabitat.gob.ar.",
)

password = reqparse.Argument(
    "Geoserver Password",
    dest="pass",
    location="form",
    type=str,
    required=True,
    help="Your password for wms.minhabitat.gob.ar.",
)

usuario_ele = reqparse.Argument(
    "Usiario del sistema de Ele",
    dest="ele",
    location="form",
    type=str,
    required=False,
    help="El usuario que se logueó en Ele, si esta request viene de Ele.",
)

def form_maker(*args):
    request_parser = reqparse.RequestParser()
    for arg in args:
        request_parser.add_argument(arg)
    return request_parser


import_kml_parser = form_maker(file, layer, username, password, usuario_ele)
