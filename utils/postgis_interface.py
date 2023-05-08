import re
from typing import Literal, Union

import sqlalchemy
from geopandas import GeoDataFrame
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker

from api.config import settings


class PostGIS:
    """
    An interface for geoserver's REST API interactions.
    """

    def __init__(
        self,
        host: str = None,
        username: str = None,
        password: str = None,
        database: str = None,
        schema: str = None,
        driver: str = None,
        *args,
        **kwargs,
    ):
        self._host = host or settings.__getattribute__("POSTGIS_HOST")
        self._username = username or settings.__getattribute__("POSTGIS_USER")
        self._password = password or settings.__getattribute__("POSTGIS_PASS")
        self._database = database or settings.__getattribute__("POSTGIS_DATABASE")
        self._schema = schema or settings.__getattribute__("POSTGIS_SCHEMA")
        self._driver = driver or settings.__getattribute__("POSTGIS_DRIVER")
        self._engine = None
        self._session = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def database(self) -> str:
        return self._database

    @property
    def schema(self) -> str:
        return self._schema

    @property
    def driver(self) -> str:
        return self._driver

    @property
    def url(self) -> sqlalchemy.URL:
        return sqlalchemy.URL.create(
            self.driver,
            username=self.username,
            password=self.password,
            host=self.host,
            database=self.database,
        )

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

    def create_engine(self) -> sqlalchemy.engine.Engine:
        self._engine = sqlalchemy.create_engine(self.url)
        self._engine.execution_options(autocommit=True)

    def create_session(self) -> sqlalchemy.orm.scoped_session:
        self._session = scoped_session(sessionmaker(bind=self.engine))

    def clean(self, query: str) -> str:
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
            # TODO: Downgrade to sqlalchemy = "^1.4.39".
            #   "sqlalchemy.exc.ObjectNotExecutableError: Not an executable object"
            #   is introduced in sqlalchemy = "^2.0.0". Execute can be done with
            #   engine in sqla 1.4.
            self.session.execute(text(query + " ;"))

    def list_tables(self) -> list:
        return sqlalchemy.inspect(self.engine).get_table_names(schema=self.schema)

    def create_table(
        self,
        tablename: str,
        data: Union[str, GeoDataFrame],
        if_exists: Literal["fail", "replace", "append"] = "fail",
    ) -> None:
        if isinstance(data, str):
            if tablename in self.list_tables():
                if if_exists.lower() == "fail":
                    raise Exception("create_table: Table {tablename} already exists!")
                if if_exists.lower() == "replace":
                    self.drop_table(tablename)
                if if_exists.lower() == "append":
                    raise Exception(
                        "create_table: Need to develop the append by query option."
                    )
                    # self.execute(f"INSERT INTO ...")
                    return
            self.execute(
                f"CREATE TABLE {self.schema}.{tablename} AS {self.clean(data)} ;"
            )
            return

        if isinstance(data, GeoDataFrame):
            data.to_postgis(
                name=tablename,
                con=self.engine,
                if_exists=if_exists,
                schema=self.schema,
                index=False,
                # dtype=str,
                chunksize=settings.DEFAULT_CHUNKSIZE,
            )
            return

        raise Exception(f"create_table: Unable to handle {type(data)} objects!")

    def drop_table(
        self,
        tablename: str,
        depends: str = "CASCADE",
        if_not_exists: Literal["fail", "ignore"] = "fail",
    ) -> None:
        if tablename in self.list_tables() and if_not_exists.lower() == "fail":
            raise Exception(f"drop_table: Table {tablename} doesn't exist!")
        self.execute(
            f"DROP TABLE IF EXISTS {self.schema}.{tablename} {depends.upper()} ;"
        )

    def append_table(
        self,
        tablename: str,
        data: Union[str, GeoDataFrame],
        if_not_exists: Literal["fail", "create"] = "fail",
    ) -> None:
        if tablename not in self.list_tables():
            raise Exception(f"append_table: Table {tablename} doesn't exist!")
        if isinstance(data, GeoDataFrame):
            data.to_postgis(
                name=tablename,
                con=self.engine,
                if_exists="append",
                schema=self.schema,
                index=False,
                dtype=str,
                chunksize=settings.DEFAULT_CHUNKSIZE,
            )
            return
        raise Exception(f"create_table: Unable to handle {type(data)} objects!")
