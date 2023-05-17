import re
from typing import Literal, Optional
from urllib.parse import quote_plus

import pandas
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from etc.config import settings
from models.tables import Layers


class PostGIS:
    """
    An interface for geoserver's REST API interactions.
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
        return self._engine

    @property
    def session(self) -> sqlalchemy.orm.scoped_session:
        if not self._session:
            self.create_session()
        return self._session

    def set(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def create_engine(self) -> None:
        self._engine = sqlalchemy.create_engine(self.url)
        self._engine.execution_options(autocommit=False)

    def create_session(self) -> None:
        self._session = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
            ),
        )

    @staticmethod
    def clean(query: str) -> str:
        # Removes line comments
        query = re.sub("--.*", " ", query)
        # Removes block comments
        query = re.sub("/[*]([*](?!/)|[^*])*[*]/", " ", query)
        # One-lines and removes extra whitespace
        query = re.sub("[ \n\t]+", " ", query)
        # Removes anything after a semicolon
        query = re.sub(";.*", "", query)
        # Gets rid on any leading or trailing whitespace.
        return query.strip()

    def execute(self, sql: str) -> None:
        for query in [
            self.clean(query) for query in sql.split(";") if self.clean(query) != ""
        ]:
            self.engine.execute(query + " ;")

    def list_tables(self) -> list:
        return sqlalchemy.inspect(self.engine).get_table_names(schema=self.schema)

    def list_views(self) -> list:
        return sqlalchemy.inspect(self.engine).get_view_names(schema=self.schema)

    def list_layers(self) -> list:
        return [value[0] for value in self.session.query(Layers.name).all()]

    def create_view(
        self, layer: str, if_exists: Literal["fail", "replace"] = "fail"
    ) -> None:
        if layer in self.list_views() and if_exists == "fail":
            raise Exception(f"View '{layer}' already exists!")
        self.execute(
            f"""
            CREATE OR REPLACE VIEW {self.schema}."{layer}" AS (
                SELECT
                    la."name" AS "layer",
                    ge."name" AS "nombre",
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
                # DELETE FROM {self.schema}.batches AS ba,
                #     USING {self.schema}.layers AS la
                #     WHERE ba.layer_id = la.id
                #     AND la.name = '{layer}';
            )
        self.execute(
            f"""
            DELETE FROM {self.schema}.layers AS la
                WHERE la.name = '{layer}';
            """
        )

    def count_layer_geometries(self, layer: str):
        return pandas.read_sql(
            f"""
            SELECT count(*) FROM {self.schema}."{layer}"
            """,
            self.engine,
        ).iloc[0, 0]

    def bbox(self, query: str, geometry_col: str = "geometry") -> dict:
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
