import re
from typing import Literal, Optional
from urllib.parse import quote_plus

import pandas
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from etc.config import settings
from models.tables import Layers, Logs


class PostGIS:
    """
    Una interfaz para interactuar con la API REST de Geoserver.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        driver: Optional[str] = None,
        coordsys: Optional[str] = None,
        *args,
        **kwargs,
    ):
        """
        Inicializa un objeto PostGIS.

        Args:
            host (Optional[str]): Host del servidor PostGIS.
            username (Optional[str]): Nombre de usuario para autenticación.
            password (Optional[str]): Contraseña para autenticación.
            database (Optional[str]): Nombre de la base de datos.
            schema (Optional[str]): Esquema de PostGIS.
            driver (Optional[str]): Driver de conexión (por defecto: "postgres").
            coordsys (Optional[str]): Sistema de coordenadas (por defecto: "EPSG:4326").
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        """
        self._host = host or settings.__getattribute__("POSTGIS_HOST")
        self._username = username or settings.__getattribute__("POSTGIS_USER")
        self._password = password or settings.__getattribute__("POSTGIS_PASS")
        self._database = database or settings.__getattribute__("POSTGIS_DATABASE")
        self._schema = schema or settings.__getattribute__("POSTGIS_SCHEMA")
        self._driver = driver or settings.__getattribute__("POSTGIS_DRIVER")
        self._coordsys = (
            coordsys or settings.__getattribute__("COORDINATE_SYSTEM") or "EPSG:4326"
        )
        self._engine = None
        self._session = None

    @property
    def host(self) -> Optional[str]:
        return self._host

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def password(self) -> Optional[str]:
        return self._password

    @property
    def database(self) -> Optional[str]:
        return self._database

    @property
    def schema(self) -> Optional[str]:
        return self._schema

    @property
    def driver(self) -> Optional[str]:
        return self._driver

    @property
    def coordsys(self) -> Optional[str]:
        return self._coordsys

    @property
    def coordsysid(self) -> Optional[int]:
        if not self.coordsys or not re.findall(r"\d+", self.coordsys):
            return None
        return int("".join(re.findall(r"\d+", self.coordsys)))

    @property
    def url(self) -> str:
        return (
            f"{self.driver}://{self.username}:"
            + f"{quote_plus(self.password)}@{self.host}/{self.database}"
        )

    @property
    def url_for_alembic(self) -> str:
        return self.url.replace("%", "%%")

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        if not self._engine:
            self.create_engine()
            # self._engine.execution_options = {"options": "-c timezone=utc"}
        return self._engine

    @property
    def session(self) -> sqlalchemy.orm.scoped_session:
        if not self._session:
            self.create_session()
        return self._session

    def set(self, **kwargs) -> None:
        """
        Establece los atributos del objeto.

        Args:
            **kwargs: Argumentos clave y valor para establecer los atributos del objeto.

        """
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def create_engine(self) -> None:
        """
        Crea un motor SQLAlchemy.

        """
        self._engine = sqlalchemy.create_engine(self.url)
        self._engine.execution_options(autocommit=False)

    def create_session(self) -> None:
        """
        Crea una sesión SQLAlchemy.

        """
        self._session = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
            ),
        )

    @staticmethod
    def clean(query: str) -> str:
        """
        Limpia una consulta SQL de comentarios y espacios en blanco.

        Args:
            query (str): Consulta SQL.

        Returns:
            str: Consulta SQL limpia.

        """
        # Elimina comentarios de línea
        query = re.sub("--.*", " ", query)
        # Elimina comentarios de bloque
        query = re.sub("/[*]([*](?!/)|[^*])*[*]/", " ", query)
        # Una línea y elimina espacios en blanco adicionales
        query = re.sub("[ \n\t]+", " ", query)
        # Elimina cualquier cosa después de un punto y coma
        query = re.sub(";.*", "", query)
        # Elimina espacios en blanco al comienzo y al final.
        return query.strip()

    def execute(self, sql: str) -> None:
        """
        Ejecuta una consulta SQL en el motor SQLAlchemy.

        Args:
            sql (str): Consulta SQL.

        """
        for query in [
            self.clean(query) for query in sql.split(";") if self.clean(query) != ""
        ]:
            self.engine.execute(query + " ;")

    def list_tables(self) -> list:
        """
        Obtiene una lista de nombres de tablas en el esquema.

        Returns:
            list: Lista de nombres de tablas.

        """
        return sqlalchemy.inspect(self.engine).get_table_names(schema=self.schema)

    def list_views(self) -> list:
        """
        Obtiene una lista de nombres de vistas en el esquema.

        Returns:
            list: Lista de nombres de vistas.

        """
        return sqlalchemy.inspect(self.engine).get_view_names(schema=self.schema)

    def list_layers(self) -> list:
        """
        Obtiene una lista de nombres de capas.

        Returns:
            list: Lista de nombres de capas.

        """
        return [value[0] for value in self.session.query(Layers.name).all()]

    def create_view(
        self, layer: str, if_exists: Literal["fail", "replace"] = "fail"
    ) -> None:
        """
        Crea una vista en la base de datos.

        Args:
            layer (str): Nombre de la vista.
            if_exists (Literal["fail", "replace"]): Acción a realizar si la vista ya existe
                (por defecto: "fail").

        Raises:
            Exception: Si la vista ya existe y se estableció `if_exists` en "fail".

        """
        if layer in self.list_views() and if_exists == "fail":
            raise Exception(f"View '{layer}' already exists!")
        self.execute(
            f"""
            CREATE OR REPLACE VIEW {self.schema}."{layer}" AS (
                SELECT
                    ge."name" AS "nombre",
                    ba."obra" AS "obra",
                    ba."operatoria" AS "operatoria",
                    ba."provincia" AS "provincia",
                    ba."departamento" AS "departamento",
                    ba."municipio" AS "municipio",
                    ba."localidad" AS "localidad",
                    ba."estado" AS "estado",
                    ba."descripcion" AS "descripción",
                    ba."cantidad" AS "cantidad",
                    ba."categoria" AS "categoría",
                    ba."ente" AS "ente",
                    ba."fuente" AS "fuente",
                    la."name" AS "layer",
                    ge."geometry" AS "geometry"
                FROM {self.schema}.layers AS la
                    JOIN {self.schema}.batches AS ba ON la.id = ba.layer_id
                    JOIN {self.schema}.geometries AS ge ON ba.id = ge.batch_id
                WHERE la.name = '{layer}')
            """
        )

    def drop_view(
        self,
        layer: str,
        if_not_exists: Literal["fail", "ignore"] = "fail",
        cascade: bool = False,
    ) -> None:
        """
        Elimina una vista de la base de datos.

        Args:
            layer (str): Nombre de la vista.
            if_not_exists (Literal["fail", "ignore"]): Acción a realizar si la vista no existe
                (por defecto: "fail").
            cascade (bool): Especifica si se deben eliminar las dependencias de la vista
                (por defecto: False).

        Raises:
            Exception: Si la vista no existe y se estableció `if_not_exists` en "fail".

        """
        if layer not in self.list_views() and if_not_exists == "fail":
            raise Exception(f"View '{layer}' doesn't exist!")
        self.execute(
            f"""
            DROP VIEW IF EXISTS {self.schema}."{layer}" {'CASCADE' if cascade else ''}
            """
        )

    def drop_layer(
        self,
        layer: str,
        if_not_exists: Literal["fail", "ignore"] = "fail",
        cascade: bool = False,
    ) -> None:
        """
        Elimina una capa de la base de datos.

        Args:
            layer (str): Nombre de la capa.
            if_not_exists (Literal["fail", "ignore"]): Acción a realizar si la capa no existe
                (por defecto: "fail").
            cascade (bool): Especifica si se deben eliminar las geometrías asociadas a la capa
                (por defecto: False).

        Raises:
            Exception: Si la capa no existe y se estableció `if_not_exists` en "fail".

        """
        if layer not in self.list_layers() and if_not_exists == "fail":
            raise Exception(f"Layer '{layer}' doesn't exist!")
        if cascade:
            self.execute(
                f"""
                DELETE FROM {self.schema}.geometries AS ge
                    USING {self.schema}.batches AS ba,
                    {self.schema}.layers AS la
                    WHERE ge.batch_id = ba.id
                    AND ba.layer_id = la.id
                    AND la.name = '{layer}';
                """
            )
        self.execute(
            f"""
            DELETE FROM {self.schema}.layers AS la
                WHERE la.name = '{layer}';
            """
        )

    def count_layer_geometries(self, layer: str):
        """
        Obtiene el número de geometrías en una capa.

        Args:
            layer (str): Nombre de la capa.

        Returns:
            int: Número de geometrías en la capa.

        """
        return pandas.read_sql(
            f"""
            SELECT count(*) FROM {self.schema}."{layer}"
            """,
            self.engine,
        ).iloc[0, 0]

    def bbox(self, query: str, geometry_col: str = "geometry") -> dict:
        """
        Obtiene los límites de una geometría.

        Args:
            query (str): Consulta SQL que devuelve una geometría.
            geometry_col (str): Nombre de la columna que contiene la geometría
                (por defecto: "geometry").

        Returns:
            dict: Límites de la geometría.

        """
        table = f"({self.clean(query)}) AS query_result"
        if query in self.list_views():
            table = f'"{self.schema}"."{query}"'
        blist = (
            pandas.read_sql(
                f"SELECT ST_Extent({geometry_col}) AS bbox_str FROM {table};",
                self.engine,
            )
            .iloc[0, 0]
            .strip("BOX()")
            .replace(" ", ",")
            .split(",")
        )
        return {
            "minx": float(blist[0].strip()),
            "maxx": float(blist[1].strip()),
            "miny": float(blist[2].strip()),
            "maxy": float(blist[3].strip()),
        }

    def get_layer(self, name: str) -> Layers:
        """
        Obtiene una capa de la base de datos.

        Args:
            name (str): Nombre de la capa.

        Returns:
            Layers: Objeto de capa correspondiente al nombre proporcionado.
        """
        return self.session.query(Layers).filter_by(name=name).first()

    def get_log(self, id: int) -> Logs:
        return self.session.query(Logs).get(id)

    def get_log_record(self, id: int) -> dict:
        """
        Obtiene el registro de un registro de registro de la base de datos.

        Args:
            id (int): ID del registro.

        Returns:
            dict: Registro correspondiente al ID proporcionado.
        """
        return getattr(self.get_log(id=id), "record", None)
