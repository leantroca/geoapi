from typing import Literal, Union
from urllib.parse import urlparse

import requests

from etc.config import settings


class Geoserver:
    """
    Una interfaz para interactuar con la API REST de Geoserver.
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
        """
        Inicializa un objeto Geoserver.

        Args:
            base_url (str): URL base del servidor Geoserver.
            username (str): Nombre de usuario para autenticación.
            password (str): Contraseña para autenticación.
            workspace (str): Espacio de trabajo de Geoserver.
            datastore (str): Almacenamiento de datos de Geoserver.
            coordsys (str): Sistema de coordenadas (por defecto: "EPSG:4326").
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        """
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

    @property
    def status(self) -> bool:
        try:
            response = requests.get(
                f"{self.rest_url}/about/system-status",
                auth=(self.username, self.password)
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def set(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def list_layers(self) -> list:
        """
        Obtiene una lista de capas disponibles en Geoserver.

        Returns:
            list: Lista de nombres de capas.

        """
        response = requests.get(
            f"{self.rest_url}/workspaces/{self.workspace}/layers.json",
            auth=(self.username, self.password)
        )
        response.raise_for_status()
        if not (isinstance(response.json().get("layers"), dict) and "layer" in response.json()["layers"]):
            return []
        return [
            layer["name"]
            for layer in response.json()["layers"]["layer"]
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
        Agrega una capa a Geoserver.

        Args:
            layer (str): Nombre de la capa.
            minx (Union[float, str]): Valor mínimo en el eje X (por defecto: -73.4154357571).
            maxx (Union[float, str]): Valor máximo en el eje X (por defecto: -55.25).
            miny (Union[float, str]): Valor mínimo en el eje Y (por defecto: -53.628348965).
            maxy (Union[float, str]): Valor máximo en el eje Y (por defecto: -21.8323104794).
            if_exists (Literal["fail", "replace"]): Acción a realizar si la capa ya existe
                (por defecto: "fail").

        Raises:
            Exception: Si la capa ya existe y se estableció `if_exists` en "fail".

        Otros parámetros:
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

    def delete_layer(
        self,
        layer: str,
        if_not_exists: Literal["fail", "ignore"] = "fail",
    ) -> None:
        """
        Elimina una capa de Geoserver.

        Args:
            layer (str): Nombre de la capa.
            if_not_exists (Literal["fail", "ignore"]): Acción a realizar si la capa no existe
                (por defecto: "fail").

        Raises:
            Exception: Si la capa no existe y se estableció `if_not_exists` en "fail".

        """
        if layer not in self.list_layers():
            if if_not_exists == "fail":
                raise Exception(f"Layer '{layer}' doesn't exist!")
            elif if_not_exists == "ignore":
                return
        response = requests.delete(
            f"{self.rest_url}/layers/{self.workspace}:{layer}.xml",
            auth=(self.username, self.password),
        )
        response.raise_for_status()
        response = requests.delete(
            f"{self.rest_url}/workspaces/{self.workspace}/datastores/"
            + f"{self.datastore}/featuretypes/{layer}.xml",
            auth=(self.username, self.password),
        )
        response.raise_for_status()
