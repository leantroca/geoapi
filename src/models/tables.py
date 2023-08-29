from datetime import datetime
from urllib.parse import urlparse

import pytz
from geoalchemy2 import Geometry
from sqlalchemy import MetaData, event
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, String

from utils.config import settings
from utils.general import clean_nones

# def clean_nones(kwargs: dict) -> dict:
#     return {key: value for key, value in kwargs.items() if value not in [None, {}]}


def declarative_base(cls):
    return declarative.declarative_base(
        cls=cls,
        metadata=MetaData(
            schema=settings.POSTGIS_SCHEMA,
        ),
    )


@declarative_base
class Base(object):
    """
    Clase base para las definiciones de tablas en SQLAlchemy.

    Atributos:
        id (Column): Columna de tipo entero que actúa como clave primaria.
        created_at (Column): Columna de tipo DateTime que registra la fecha y hora de creación de la entidad.
        updated_at (Column): Columna de tipo DateTime que registra la fecha y hora de actualización de la entidad.
        __table_args__ (dict): Opciones adicionales para la tabla, en este caso se establece 'extend_existing' en True.

    Propiedades:
        date (str): Propiedad que devuelve la fecha de creación en formato "%Y-%m-%d %H:%M:%S".

    """

    __table_args__ = {"extend_existing": True}
    stz = pytz.timezone(settings.POSTGIS_TIMEZONE)
    ctz = pytz.timezone(settings.CLIENT_TIMEZONE)

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime,
        default=func.now(tz=stz),
        server_default=func.now(tz=stz),
    )
    updated_at = Column(
        DateTime,
        default=func.now(tz=stz),
        onupdate=func.now(tz=stz),
        server_default=func.now(tz=stz),
        index=True,
    )

    @property
    def created(self):
        """
        Afirma que las fechas del servidor estén expresadas condiderando timezones.
        """
        if self.created_at:
            return self.stz.localize(self.created_at)
        return self.created_at

    @property
    def updated(self):
        """
        Afirma que las fechas del servidor estén expresadas condiderando timezones.
        """
        if self.updated_at:
            return self.stz.localize(self.updated_at)
        return self.updated_at

    @property
    def timestamp(self):
        """
        Devuelve la fecha de creación de la entidad en formato "%Y-%m-%d %H:%M:%S".

        Returns:
            str: Fecha de creación de la entidad.

        """
        timestamp = self.created or datetime.now(tz=self.stz)
        return timestamp.astimezone(self.ctz).strftime(
            f"%Y-%m-%d %H:%M:%S ({self.ctz.zone} UTC%Z)"
        )


class Layers(Base):
    """
    Definición de tabla para capas (layers).

    Atributos:
        __tablename__ (str): Nombre de la tabla en la base de datos.
        name (Column): Columna de tipo String que representa el nombre de la capa.
    """

    __tablename__ = "layers"

    name = Column(String, nullable=False, unique=True)
    # style_id = Column(
    #     Integer, ForeignKey("styles.id", ondelete="RESTRICT"), nullable=True
    # )
    # style = relationship("Styles", backref="layers")


class Batches(Base):
    """
    Definición de tabla para lotes (batches).

    Atributos:
        __tablename__ (str): Nombre de la tabla en la base de datos.
        obra (Column): Columna de tipo String que representa la obra.
        operatoria (Column): Columna de tipo String que representa la operatoria.
        provincia (Column): Columna de tipo String que representa la provincia.
        departamento (Column): Columna de tipo String que representa el departamento.
        municipio (Column): Columna de tipo String que representa el municipio.
        localidad (Column): Columna de tipo String que representa la localidad.
        estado (Column): Columna de tipo String que representa el estado.
        descripcion (Column): Columna de tipo String que representa la descripción.
        cantidad (Column): Columna de tipo String que representa la cantidad.
        categoria (Column): Columna de tipo String que representa la categoría.
        ente (Column): Columna de tipo String que representa el ente.
        fuente (Column): Columna de tipo String que representa la fuente.
        json (Column): Columna de tipo JSON que almacena datos adicionales en formato JSON.
        layer_id (Column): Columna de tipo Integer que representa la clave externa a la tabla de capas.
        layer (relationship): Relación con la tabla de capas (Layers).
        record (property): Propiedad que devuelve un diccionario con los campos relevantes del lote.

    """

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
        """
        Devuelve un diccionario con los campos relevantes del lote.

        Returns:
            dict: Diccionario con los campos relevantes del lote.

        """
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
                "timestamp": self.timestamp,
            }
        )


class Geometries(Base):
    """
    Definición de tabla para geometrías (geometries).

    Atributos:
        __tablename__ (str): Nombre de la tabla en la base de datos.
        geometry (Column): Columna de tipo Geometry que representa la geometría.
        name (Column): Columna de tipo String que representa el nombre de la geometría.
        description (Column): Columna de tipo String que representa la descripción de la geometría.
        json (Column): Columna de tipo JSON que almacena datos adicionales en formato JSON.
        batch_id (Column): Columna de tipo Integer que representa la clave externa a la tabla de lotes.
        batch (relationship): Relación con la tabla de lotes (Batches).

    """

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
    """
    Definición de tabla para registros de registro (logs).

    Atributos:
        __tablename__ (str): Nombre de la tabla en la base de datos.
        endpoint (Column): Columna de tipo String que representa el endpoint.
        layer (Column): Columna de tipo String que representa la capa.
        status (Column): Columna de tipo String que representa el estado.
        message (Column): Columna de tipo String que representa el mensaje.
        url (Column): Columna de tipo String que representa la URL.
        json (Column): Columna de tipo JSON que almacena datos adicionales en formato JSON.
        batch_id (Column): Columna de tipo Integer que representa la clave externa a la tabla de lotes.
        batch (relationship): Relación con la tabla de lotes (Batches).
        record (property): Propiedad que devuelve un diccionario con los campos relevantes del registro.
        update (method): Método que actualiza los valores de los atributos.
        message_append (method): Método que agrega un mensaje adicional al mensaje existente.

    """

    __tablename__ = "logs"

    endpoint = Column(String, nullable=True, default=None)
    layer = Column(String, nullable=True, default=None)
    status = Column(Integer, nullable=True, default=None)
    message = Column(String, nullable=True, default=None)
    url = Column(String, nullable=True, default=None)
    json = Column(JSON, nullable=True, default=None)

    batch_id = Column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=True
    )
    batch = relationship("Batches", backref="logs")
    # style_id = Column(
    #     Integer, ForeignKey("styles.id", ondelete="RESTRICT"), nullable=True
    # )
    # style = relationship("Styles", backref="logs")

    def __init__(self):
        Base.__init__(self)
        self.url = self.get_url()

    def update(self, *args, **kwargs):
        """
        Actualiza los valores de los atributos con los valores proporcionados en kwargs.

        Args:
            *args: Argumentos posicionales (no utilizados).
            **kwargs: Argumentos de palabras clave con los nuevos valores de los atributos.

        """
        for key, value in kwargs.items():
            if hasattr(self, f"{key}"):
                setattr(self, f"{key}", value)
            if key == "append_message":
                self.message_append(value)

    def get_url(self):
        return (
            urlparse(settings.BASE_URL)
            ._replace(path=f"/status/record/{self.id}")
            .geturl()
            if self.id
            else None
        )

    @property
    def record(self):
        """
        Devuelve un diccionario con los campos relevantes del registro.

        Returns:
            dict: Diccionario con los campos relevantes del registro.

        """
        return clean_nones(
            {
                "endpoint": self.endpoint,
                "status": self.status,
                "message": self.message,
                "url": self.url,
                "timestamp": self.timestamp,
                "metadata": self.json,
                "batch": self.batch.record if self.batch else None,
                # "style": self.style.record if self.style else None,
            }
        )

    def message_append(self, message: str) -> None:
        """
        Agrega un mensaje adicional al mensaje existente.

        Args:
            message (str): Mensaje adicional a agregar.

        """
        self.message = (
            ". ".join([(self.message or "").strip(". "), message.strip(". ")]) + "."
        )


@event.listens_for(Logs, "before_update")
def autoupdate_logs(mapper, connection, log):
    log.url = log.get_url()


# class Styles(Base):
#     """
#     Definición de tabla para estilos (styles).

#     Atributos:
#         __tablename__ (str): Nombre de la tabla en la base de datos.
#         name (Column): Columna de tipo String que representa el nombre del estilo.
#     """

#     __tablename__ = "styles"

#     name = Column(String, nullable=False, unique=True)
