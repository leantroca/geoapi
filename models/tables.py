from urllib.parse import urlparse

import pytz
from geoalchemy2 import Geometry
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, String

from etc.config import settings


def clean_nones(kwargs: dict) -> dict:
    return {
        key: value for key, value in kwargs.items() if value is not None and value != {}
    }


def declarative_base(cls):
    return declarative.declarative_base(
        cls=cls,
        metadata=MetaData(
            schema=settings.POSTGIS_SCHEMA,
        ),
    )


@declarative_base
class Base(object):
    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime,
        default=func.now(tz=pytz.timezone("America/Buenos_Aires")),
        server_default=func.now(tz=pytz.timezone("America/Buenos_Aires")),
    )
    updated_at = Column(
        DateTime,
        default=func.now(tz=pytz.timezone("America/Buenos_Aires")),
        onupdate=func.now(tz=pytz.timezone("America/Buenos_Aires")),
        server_default=func.now(tz=pytz.timezone("America/Buenos_Aires")),
        index=True,
    )
    __table_args__ = {"extend_existing": True}

    @property
    def date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")


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

    layer_id = Column(
        Integer, ForeignKey("layers.id", ondelete="SET NULL"), nullable=True
    )
    layer = relationship("Layers", backref="batches")

    @property
    def record(self):
        return clean_nones(
            {
                "id": self.id,
                "layer": self.layer.name,
                "geometries": len(self.geometries),
                "obra": self.obra,
                "operatoria": self.operatoria,
                "provincia": self.provincia,
                "departamento": self.departamento,
                "municipio": self.municipio,
                "localidad": self.localidad,
                "estado": self.estado,
                "descripcion": self.descripcion,
                "cantidad": self.cantidad,
                "categoria": self.categoria,
                "ente": self.ente,
                "fuente": self.fuente,
                "json": self.json,
                "timestamp": self.date,
            }
        )


class Geometries(Base):
    __tablename__ = "geometries"

    geometry = Column(
        Geometry(
            "GEOMETRYZ",
            srid=int(settings.COORDINATE_SYSTEM.split(":")[-1]),
            dimension=3,
        ),
        nullable=False,
    )
    name = Column(String, nullable=True, default=None)
    description = Column(String, nullable=True, default=None)
    json = Column(JSON, nullable=True, default=None)

    batch_id = Column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=True
    )
    batch = relationship("Batches", backref="geometries")


class Logs(Base):
    __tablename__ = "logs"

    endpoint = Column(String, nullable=True, default=None)
    layer = Column(String, nullable=True, default=None)
    status = Column(String, nullable=True, default=None)
    message = Column(String, nullable=True, default=None)
    url = Column(String, nullable=True, default=None)
    json = Column(JSON, nullable=True, default=None)

    batch_id = Column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=True
    )
    batch = relationship("Batches", backref="logs")

    def update(self, *args, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, f"{key}"):
                setattr(self, f"{key}", value)

    @property
    def record(self):
        return clean_nones(
            {
                "endpoint": self.endpoint,
                "status": self.status,
                "message": self.message,
                "url": urlparse(settings.BASE_URL)
                ._replace(path=f"/status/batch/{self.id}")
                .geturl(),
                "timestamp": self.date,
                "json": self.json,
                "batch": self.batch.record if self.batch else None,
            }
        )

    def message_append(self, message: str) -> None:
        self.message = ". ".join([self.message.strip(". "), message.strip(". ")]) + "."
