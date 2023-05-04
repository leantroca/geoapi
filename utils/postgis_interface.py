import re

import sqlalchemy
from geopandas import GeoDataFrame

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

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def database(self):
        return self._database

    @property
    def schema(self):
        return self._schema

    @property
    def driver(self):
        return self._driver

    @property
    def url(self):
        return sqlalchemy.URL.create(
            self.driver,
            username=self.username,
            password=self.password,
            host=self.host,
            database=self.database,
        )

    @property
    def engine(self):
        if not self._engine:
            self.create_engine()
        return self._engine

    def set(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def create_engine(self):
        self._engine = sqlalchemy.create_engine(self.url)

    def clean(self, query: str):
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

    def execute(self, sql: str):
        for query in [
            self.clean(query) for query in sql.split(";") if self.clean(query) != ""
        ]:
            self.engine.execute(query + " ;")

    def list_tables(self):
        return sqlalchemy.inspect(self.engine).get_table_names(schema=self.schema)

    def create_table(self, tablename: str, data: object, if_exists: str = "fail"):
        if isinstance(data, str):
            if tablename in self.list_tables():
                if if_exists.lower() == "fail":
                    raise Exception("Table {tablename} already exists!")
                if if_exists.lower() == "replace":
                    self.drop_table(tablename)
                if if_exists.lower() == "append":
                    raise Exception("Need to develop the append by query option.")
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
                dtype=str,
                chunksize=settings.DEFAULT_CHUNKSIZE,
            )
            return

    def drop_table(
        self, tablename: str, depends: str = "CASCADE", if_not_exists: str = "error"
    ):
        if tablename in self.list_tables() and if_not_exists.lower() == "error":
            raise Exception(f"Table {tablename} doesn't exist!")
        self.execute(
            f"DROP TABLE IF EXISTS {self.schema}.{tablename} {depends.upper()} ;"
        )
