from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, String

from utils.postgis_interface import PostGIS

postgis = PostGIS()

engine = postgis.engine


def declarative_base(cls):
	return declarative.declarative_base(
		cls=cls,
		metadata=MetaData(
			schema=postgis.schema,
		),
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

	name = Column(String, nullable=False, unique=True)


class Batches(Base):
	__tablename__ = "batches"

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

	layer_id = Column(Integer, ForeignKey("layers.id"), nullable=True)
	layer = relationship("Layers", backref="batches")


class Geometries(Base):
	__tablename__ = "geometries"

	geometry = Column(Geometry("GEOMETRYZ", srid=postgis.coordsysid, dimension=3), nullable=False)
	name = Column(String, nullable=True, default=None)
	description = Column(String, nullable=True, default=None)
	json = Column(JSON, nullable=True, default=None)

	batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
	batch = relationship("Batches", backref="geometries")


class Logs(Base):
	__tablename__ = "logs"

	endpoint = Column(String, nullable=True, default=None)
	status = Column(String, nullable=True, default=None)
	message = Column(String, nullable=True, default=None)
	url = Column(String, nullable=True, default=None)
	json = Column(JSON, nullable=True, default=None)

	batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
	batch = relationship("Batches", backref="logs")
