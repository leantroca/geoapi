import re
from typing import List, Literal, Optional, Union
from urllib.parse import quote_plus

import pandas
import sqlalchemy
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import scoped_session, sessionmaker

from models.tables import Batches, Geometries, Layers, Logs
from utils.config import settings


class PostGIS:
    """
    Una interfaz para interactuar con la API REST de Geoserver.
    """

    def __init__(
        self,
        host: Optional[str] = settings.__getattribute__("POSTGIS_HOSTNAME"),
        port: Optional[int] = settings.__getattribute__("POSTGIS_PORT"),
        username: str = settings.__getattribute__("POSTGIS_USER"),
        password: str = settings.__getattribute__("POSTGIS_PASS"),
        database: str = settings.__getattribute__("POSTGIS_DATABASE"),
        schema: str = settings.__getattribute__("POSTGIS_SCHEMA"),
        driver: str = settings.__getattribute__("POSTGIS_DRIVER")
        or "postgresql+psycopg2",
        coordsys: str = settings.__getattribute__("COORDINATE_SYSTEM") or "EPSG:4326",
        pool_size: int = 10,
        pool_recycle: int = 1500,
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
        self._host = host + (f":{port}" if port else "")
        self._username = username
        self._password = password
        self._database = database
        self._schema = schema
        self._driver = driver
        self._coordsys = coordsys
        self._engine = None
        self._session = None
        self._pool_size = pool_size
        self._pool_recycle = pool_recycle

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if not exc_type:
                self.session.commit()
            else:
                if isinstance(exc_value, DatabaseError):
                    print("Error occurred, rolling back changes...")
                    self.session.rollback()
                else:
                    raise
        finally:
            self.session.close()

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
        return self._engine

    @property
    def session(self) -> sqlalchemy.orm.scoped_session:
        if not self._session:
            self.create_session()
        return self._session

    @property
    def status(self) -> bool:
        try:
            self.engine.connect()
            self.list_tables()
        except sqlalchemy.exc.OperationalError:
            return False
        return True

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
        self._engine = sqlalchemy.create_engine(
            self.url,
            poolclass=sqlalchemy.pool.QueuePool,
            pool_size=self._pool_size,
            pool_recycle=self._pool_recycle,
        )
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
        self.session.commit()

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

    def drop_batches(
        self,
        ids: Union[int, List[int]],
        cascade: bool = False,
    ):
        """
        Elimina Batches según una lista de ids. Si se ejecuta en modo
        cascade: elimina geometrías que dependen de los batches y anula relaciones
        con Logs generados.
        """
        # Assert to deal with a list of indexes
        if isinstance(ids, int):
            ids = [ids]
        geometries_deleted = 0
        with self.engine.begin() as transaction:
            geometries_remaining = (
                self.session.query(Geometries)
                .filter(Geometries.batch_id.in_(ids))
                .count()
            )
            if cascade:
                geometries_deleted = geometries_remaining
                # Run cascade efect
                transaction.execute(
                    """
                        UPDATE {schema}.logs
                        SET batch_id = NULL
                        WHERE batch_id IN ({ids}) ;
                    """.format(
                        schema=self.schema, ids=", ".join(str(i) for i in ids)
                    )
                )
                transaction.execute(
                    """
                        DELETE FROM {schema}.geometries
                        WHERE batch_id IN ({ids}) ;
                    """.format(
                        schema=self.schema, ids=", ".join(str(i) for i in ids)
                    )
                )
            elif geometries_remaining > 0:
                raise Exception(
                    f"Batch deletion prevented! There are {geometries_remaining} geometries attached to"
                    " this batch. Set 'cascade' to true to proceed with Geometry deletion as well."
                )
            # Delete batches
            transaction.execute(
                """
                    DELETE FROM {schema}.geometries
                    WHERE batch_id IN ({ids}) ;
                """.format(
                    schema=self.schema, ids=", ".join(str(i) for i in ids)
                )
            )
            # self.session.commit()
        return geometries_deleted

    def drop_geometries(
        self,
        ids: Union[int, List[int]],
        cascade: bool = False,
    ):
        """
        Elimina geometrías en base a una lista de ids.
        """
        if isinstance(ids, int):
            ids = [ids]
        geometries_deleted = (
            self.session.query(Geometries).filter(Geometries.id.in_(ids)).count()
        )
        with self.engine.begin() as transaction:
            transaction.execute(
                """
                    DELETE FROM {schema}.geometries
                    WHERE id IN ({ids}) ;
                """.format(
                    schema=self.schema, ids=", ".join(str(i) for i in ids)
                )
            )
            # self.session.commit()
        return geometries_deleted

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
        if query.strip() in self.list_views():
            table = f'{self.schema}."{query.strip()}"'
        else:
            table = f"({self.clean(query)}) AS query_result"
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

    def get_log(self, id: Union[int, Logs]) -> Logs:
        return self.session.query(Logs).get(id) if isinstance(id, int) else id

    def get_log_record(self, id: int) -> dict:
        """
        Obtiene el registro de un registro de registro de la base de datos.

        Args:
            id (int): ID del registro.

        Returns:
            dict: Registro correspondiente al ID proporcionado.
        """
        return getattr(self.get_log(id=id), "record", None)

    def get_batch(self, id: Union[int, Batches]) -> Batches:
        return self.session.query(Batches).get(id) if isinstance(id, int) else id

    def get_batch_record(self, id: int) -> dict:
        """
        Obtiene el registro de un registro de batch de la base de datos.

        Args:
            id (int): ID del batch.

        Returns:
            dict: Registro correspondiente al ID proporcionado.
        """
        return getattr(self.get_batch(id=id), "record", None)

    def get_layer(
        self, id: Optional[int] = None, name: Optional[str] = None
    ) -> Optional[Layers]:
        """
        Devuelve el objeto de una capa existente.

        Args:
            id (int, opcional): ID de la capa a buscar.
            name (str, opcional): Nombre de la capa a buscar.

        Returns:
            Layers o None: Objeto de la capa si se encuentra,
                o None si no se encuentra ninguna coincidencia.
        """
        if id:
            return self.session.query(Layers).get(id) if isinstance(id, int) else id
        elif name:
            return self.session.query(Layers).filter_by(name=name).first()
        else:
            return None

    def get_or_create_layer(
        self, id: Optional[int] = None, name: Optional[str] = None
    ) -> Layers:
        """
        Devuelve el objeto de una capa existente o la crea en caso de no existir.

        Args:
            id (int, opcional): ID de la capa a buscar o crear.
            name (str, opcional): Nombre de la capa a buscar o crear.

        Returns:
            Layers: Objeto de la capa existente o recién creada.
        """
        return self.get_layer(id=id, name=name) or Layers(name=name)
