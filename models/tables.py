from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String, Unicode
from sqlalchemy.ext import declarative
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from etc.config import settings
from utils.postgis_interface import PostGIS
from datetime import datetime
from sqlalchemy import MetaData


postgis = PostGIS()

engine = postgis.engine

def declarative_base(cls):
	return declarative.declarative_base(
		cls=cls,
		metadata=MetaData(
			schema=postgis.schema,
		)
	)


@declarative_base
class Base(object):
	id = Column(Integer, primary_key=True)
	created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
	updated_at = Column(
		DateTime,
		default=datetime.utcnow,
		onupdate=datetime.utcnow,
		server_default=func.now(),
		index=True,
	)


class Layers(Base):
	__tablename__ = "layers"

	name = Column(String, nullable=False)
	obra = Column(String, nullable=True, default=None)
	operatoria = Column(String, nullable=True, default=None)
	provincia = Column(String, nullable=True, default=None)
	departamento = Column(String, nullable=True, default=None)
	municipio = Column(String, nullable=True, default=None)
	localidad = Column(String, nullable=True, default=None)
	estado = Column(String, nullable=True, default=None)
	descripcion = Column(String, nullable=True, default=None)
	cantidad = Column(String, nullable=True, default=None)
	categoria = Column(String, nullable=True, default=None)
	ente = Column(String, nullable=True, default=None)
	fuente = Column(String, nullable=True, default=None)
	json = Column(JSON, nullable=True, default=None)


class Geometries(Base):
	__tablename__ = "geometries"

	geometry = Column(Geometry("GEOMETRY", srid=postgis.coordsysid))
	name = Column(String, nullable=True, default=None)
	description = Column(String, nullable=True, default=None)
	json = Column(JSON, nullable=True, default=None)

	layer_id = Column(Integer, ForeignKey("layers.id"), nullable=True)

	layer = relationship("Layers", backref="geometry_ids")

