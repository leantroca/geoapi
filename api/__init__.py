from flask import Blueprint
from flask_restx import Api

from .geoserver import namespace

endpoints = Blueprint("api", __name__)
api = Api(endpoints)

api.add_namespace(namespace, path="/geoserver")
