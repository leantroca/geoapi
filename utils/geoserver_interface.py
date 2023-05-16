from typing import Literal, Union
from urllib.parse import urlparse

import requests

from etc.config import settings


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
        coordsys: str = None,
        *args,
        **kwargs,
    ):
        self._base_url = base_url or settings.__getattribute__("GEOSERVER_BASE_URL")
        self._username = username or settings.__getattribute__("GEOSERVER_USERNAME")
        self._password = password or settings.__getattribute__("GEOSERVER_PASSWORD")
        self._workspace = workspace or settings.__getattribute__("GEOSERVER_WORKSPACE")
        self._datastore = datastore or settings.__getattribute__("GEOSERVER_DATASTORE")
        self._coordsys = (
            coordsys or settings.__getattribute__("COORDINATE_SYSTEM") or "EPSG:4326"
        )

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

    @property
    def coordsys(self) -> str:
        return self._coordsys

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

    def push_layer(
        self,
        layer: str,
        minx: Union[float, str] = -73.4154357571,
        maxx: Union[float, str] = -55.25,
        miny: Union[float, str] = -53.628348965,
        maxy: Union[float, str] = -21.8323104794,
        if_exists: Literal["fail", "replace"] = "fail",
    ):
        """
        <nativeName>my_table</nativeName>
        <title>My Table</title>
        <abstract>My table description</abstract>
        <enabled>true</enabled>
        """
        if if_exists.lower() == "fail" and layer in self.list_layers():
            raise Exception(f"Layer {layer} already exists!")
        response = requests.post(
            f"{self.rest_url}/workspaces/{self.workspace}"
            + f"/datastores/{self.datastore}/featuretypes",
            # + "?recalculate=nativebbox,latlonbbox",
            auth=(self.username, self.password),
            headers={"Content-type": "text/xml"},
            data=f"""
                <featureType>
                  <name>{layer}</name>
                  <nativeCRS>{self.coordsys}</nativeCRS>
                  <srs>{self.coordsys}</srs>
                  <nativeBoundingBox>
                    <minx>{minx}</minx>
                    <maxx>{maxx}</maxx>
                    <miny>{miny}</miny>
                    <maxy>{maxy}</maxy>
                    <crs>{self.coordsys}</crs>
                  </nativeBoundingBox>
                </featureType>
            """,
        )
        response.raise_for_status()

# http://localhost:8080/geoserver/rest/workspaces/minhabitat/layers/RE_06.json
