import re
from typing import Optional
from urllib.parse import quote_plus

import pandas
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from etc.config import settings


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
        # return sqlalchemy.URL.create(
        #     self.driver,
        #     username=self.username,
        #     password=self.password,
        #     host=self.host,
        #     database=self.database,
        # )

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

    def create_view(self, layer: str) -> None:
        self.execute(
            f"""
            CREATE OR REPLACE VIEW {self.schema}."{layer}" AS (
                SELECT
                    la."name" AS "layer",
                    ge."name" AS "nombre",
                    ge."geometry" AS "geometry"
                FROM {self.schema}.layers AS la
                JOIN {self.schema}.geometries AS ge ON la.id = ge.layer_id
                WHERE la.name = '{layer}')
            """
        )

    def bbox(self, query: str, geometry_col: str = "geometry"):
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
            "minx": blist[0],
            "maxx": blist[1],
            "miny": blist[2],
            "maxy": blist[3],
        }

    # def get_or_create(self, model, **kwargs):
    #     instance = self.session.query(model).filter_by(
    #         **{key:value for key, value in kwargs.items() \
    #         if key not in optional_arguments and key in dir(model)}
    #     ).first()
    #     if instance:
    #         return instance
    #     else:
    #         instance = model(**kwargs)
    #         self.session.add(instance)
    #         self.session.commit()
    #         return instance

    # def create_table(
    #     self,
    #     tablename: str,
    #     data: Union[str, GeoDataFrame],
    #     if_exists: Literal["fail", "replace", "append"] = "fail",
    # ) -> None:
    #     if isinstance(data, str):
    #         if tablename in self.list_tables():
    #             if if_exists.lower() == "fail":
    #                 raise Exception("create_table: Table {tablename} already exists!")
    #             if if_exists.lower() == "replace":
    #                 self.drop_table(tablename)
    #             if if_exists.lower() == "append":
    #                 raise Exception(
    #                     "create_table: Need to develop the append by query option."
    #                 )
    #                 # self.execute(f"INSERT INTO ...")
    #                 return
    #         self.execute(
    #             f"CREATE TABLE {self.schema}.{tablename} AS {self.clean(data)} ;"
    #         )
    #         return

    #     if isinstance(data, GeoDataFrame):
    #         data.to_postgis(
    #             name=tablename,
    #             con=self.engine,
    #             if_exists=if_exists,
    #             schema=self.schema,
    #             index=False,
    #             # dtype=str,
    #             chunksize=settings.DEFAULT_CHUNKSIZE,
    #         )
    #         return

    #     raise Exception(f"create_table: Unable to handle {type(data)} objects!")

    # def drop_table(
    #     self,
    #     tablename: str,
    #     depends: str = "CASCADE",
    #     if_not_exists: Literal["fail", "ignore"] = "fail",
    # ) -> None:
    #     if tablename in self.list_tables() and if_not_exists.lower() == "fail":
    #         raise Exception(f"drop_table: Table {tablename} doesn't exist!")
    #     self.execute(
    #         f"DROP TABLE IF EXISTS {self.schema}.{tablename} {depends.upper()} ;"
    #     )

    # def append_table(
    #     self,
    #     tablename: str,
    #     data: Union[str, GeoDataFrame],
    #     if_not_exists: Literal["fail", "create"] = "fail",
    # ) -> None:
    #     if tablename not in self.list_tables():
    #         raise Exception(f"append_table: Table {tablename} doesn't exist!")
    #     if isinstance(data, GeoDataFrame):
    #         data.to_postgis(
    #             name=tablename,
    #             con=self.engine,
    #             if_exists="append",
    #             schema=self.schema,
    #             index=False,
    #             dtype=str,
    #             chunksize=settings.DEFAULT_CHUNKSIZE,
    #         )
    #         return
    #     raise Exception(f"create_table: Unable to handle {type(data)} objects!")
