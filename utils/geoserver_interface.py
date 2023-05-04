from urllib.parse import urlparse

import requests

from api.config import settings


class Geoserver:
    """
    An interface for geoserver's REST API interactions.
    """

    def __init__(
        self,
        base_url: str = None,
        username: str = None,
        password: str = None,
        workspace: str = None,
        datastore: str = None,
        *args,
        **kwargs,
    ):
        self._base_url = base_url or settings.__getattribute__("GEOSERVER_BASE_URL")
        self._username = username or settings.__getattribute__("GEOSERVER_USERNAME")
        self._password = password or settings.__getattribute__("GEOSERVER_PASSWORD")
        self._workspace = workspace or settings.__getattribute__("GEOSERVER_WORKSPACE")
        self._datastore = datastore or settings.__getattribute__("GEOSERVER_DATASTORE")

    @property
    def base_url(self) -> str:
        return urlparse(self._base_url)._replace(path="/geoserver").geturl()

    @property
    def rest_url(self) -> str:
        return f"{self.base_url}/rest"

    @property
    def hostname(self) -> str:
        return urlparse(self.base_url).netloc

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def workspace(self) -> str:
        return self._workspace

    @property
    def datastore(self) -> str:
        return self._datastore

    def set(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def list_layers(self) -> list:
        return [
            layer["name"]
            for layer in requests.get(
                f"{self.rest_url}/workspaces/{self.workspace}/layers.json",
                auth=(self.username, self.password),
            ).json()["layers"]["layer"]
        ]
