import os
import re
import tempfile
from typing import Generator, Literal, Optional, Type, Union

import fiona
import geopandas
import pandas
import requests
from bs4 import BeautifulSoup
from werkzeug.datastructures import FileStorage


class KML:
    """Interfaz para archivos KML."""

    fiona.drvsupport.supported_drivers["KML"] = "rw"
    fiona.drvsupport.supported_drivers["LIBKML"] = "rw"

    def __init__(
        self,
        file: Union[str, FileStorage, geopandas.GeoDataFrame, Type["KML"]],
        driver: Optional[str] = "KML",
        chunksize: Optional[int] = None,
        optional: Optional[dict] = {},
        **kwargs,
    ):
        """
        Inicializa un manejador de archivos KML.

        Args:
                file (Union[str, FileStorage, geopandas.GeoDataFrame]): El archivo KML a manejar.
                        Puede ser una ruta de archivo (str), un objeto FileStorage o un GeoDataFrame.
                driver (Optional[str]): El driver a utilizar para leer y escribir archivos KML.
                        Por defecto es 'KML'.
                chunksize (Optional[int]): La cantidad de entidades por fragmento al leer archivos KML.
                        Si se especifica, el archivo KML se leerá en fragmentos como un generador.
                optional (Optional[dict]): Parámetros opcionales adicionales que se pasan a la función.

        Raises:
                Exception: Si el archivo no puede ser manejado.

        """
        self._driver = driver
        self._chunksize = chunksize
        optional.update(kwargs)
        self._optional = optional
        if isinstance(file, str):
            if re.match(r"^(http|https)://", file.strip().lower()):
                self._path = os.path.join(self.temp_dir, "handle.kml")
                response = requests.get(file)
                response.raise_for_status()
                with open(self._path, "wb") as writer:
                    writer.write(response.content)
                return
            self._temp_dir = None
            self._path = file
            return
        if isinstance(file, FileStorage):
            self._path = os.path.join(self.temp_dir, "handle.kml")
            file.save(self._path)
            return
        if isinstance(file, geopandas.GeoDataFrame):
            self._path = os.path.join(self.temp_dir, "handle.kml")
            file.to_file(self.path, driver=self.driver)
            return
        if self.isselfinstance(file):
            self._temp_dir = None
            self._path = file.path
            return
        raise Exception(f"file {file} of class {type(file)} can't be handled.")

    def __del__(self):
        """
        Libera los recursos utilizados por el objeto KML.

        """

        if self._temp_dir is not None:
            self._temp_dir.cleanup()

    @classmethod
    def isselfinstance(cls, obj):
        return isinstance(obj, cls)

    @property
    def temp_dir(self):
        """
        Directorio temporal utilizado para almacenar los archivos KML.

        Returns:
                str: Ruta del directorio temporal.

        """
        if getattr(self, "_temp_dir", None) is None:
            self._temp_dir = tempfile.TemporaryDirectory()
        return self._temp_dir.name

    @property
    def path(self) -> str:
        """
        Ruta del archivo KML.

        Returns:
                str: Ruta del archivo KML.

        """
        return self._path

    @property
    def driver(self) -> str:
        """
        Driver utilizado para leer y escribir archivos KML.

        Returns:
                str: Driver utilizado.

        """
        return self._driver

    @property
    def chunksize(self) -> int:
        """
        Tamaño de los fragmentos al leer archivos KML.

        Returns:
                int: Tamaño de los fragmentos.

        """
        return self._chunksize

    @property
    def optional(self) -> dict:
        """
        Parámetros opcionales adicionales para la lectura de archivos KML.

        Returns:
                dict: Parámetros opcionales adicionales.

        """
        return self._optional

    @property
    def folders(self) -> list[str]:
        """
        Lista de carpetas (layers) en el archivo KML.

        Returns:
                list[str]: Lista de carpetas en el archivo KML.

        """
        return fiona.listlayers(self.path)

    def set(self, **kwargs) -> None:
        """
        Establece los valores de los atributos de la clase.

        Args:
                **kwargs: Valores de los atributos a establecer.

        """
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def read_kml(
        self, driver: Optional[str] = None, chunksize: Optional[int] = None, **kwargs
    ) -> Union[geopandas.GeoDataFrame, Generator[geopandas.GeoDataFrame, None, None]]:
        """
        Lee el archivo KML y devuelve un GeoDataFrame o un generador de GeoDataFrames.

        Args:
            driver (Optional[str]): El driver a utilizar para leer el archivo KML.
                    Si no se especifica, se utiliza el driver establecido en la inicialización.
            chunksize (Optional[int]): La cantidad de entidades por fragmento al leer el archivo KML.
                    Si no se especifica, se utiliza el valor establecido en la inicialización.
            **kwargs: Parámetros opcionales adicionales que se pasan a la función.

        Returns:
            Union[geopandas.GeoDataFrame, Generator[geopandas.GeoDataFrame, None, None]]:
                Un GeoDataFrame si no se especifica `chunksize`, o un generador de GeoDataFrames si se especifica.

        """
        driver = driver or self.driver
        chunksize = chunksize if chunksize is not None else self.chunksize
        optional = self.optional.copy()
        optional.update(kwargs)
        if chunksize:
            return self.load_kml_in_chunks(chunksize=chunksize, **optional)
        else:
            return self.load_kml(**optional)

    def load_kml(
        self, driver: Optional[str] = None, **kwargs
    ) -> geopandas.GeoDataFrame:
        """
        Carga el archivo KML completo y devuelve un GeoDataFrame.

        Args:
                driver (Optional[str]): El driver a utilizar para leer el archivo KML.
                        Si no se especifica, se utiliza el driver establecido en la inicialización.
                **kwargs: Parámetros opcionales adicionales que se pasan a la función.

        Returns:
                geopandas.GeoDataFrame: El GeoDataFrame cargado desde el archivo KML.

        """
        driver = driver or self.driver
        optional = self.optional.copy()
        optional.update(kwargs)
        load_kml = geopandas.GeoDataFrame(
            pandas.concat(
                (
                    geopandas.read_file(
                        self.path, driver=driver, layer=folder, **optional
                    )
                    for folder in self.folders
                ),
                ignore_index=True,
            ),
        )
        return load_kml

    def load_kml_in_chunks(
        self, driver: Optional[str] = None, chunksize: Optional[int] = None, **kwargs
    ) -> Generator[geopandas.GeoDataFrame, None, None]:
        """
        Carga el archivo KML en fragmentos y devuelve un generador de GeoDataFrames.

        Args:
            driver (Optional[str]): El driver a utilizar para leer el archivo KML.
                    Si no se especifica, se utiliza el driver establecido en la inicialización.
            chunksize (Optional[int]): La cantidad de entidades por fragmento al leer el archivo KML.
                    Si no se especifica, se utiliza el valor establecido en la inicialización.
            **kwargs: Parámetros opcionales adicionales que se pasan a la función.

        Yields:
            Generator[geopandas.GeoDataFrame, None, None]: Un generador de GeoDataFrames cargados desde el archivo KML.

        """
        driver = driver or self.driver
        chunksize = chunksize or self.chunksize
        layer_list = []
        sum_chunks = 0
        for i, folder in enumerate(self.folders):
            chunk = geopandas.read_file(
                self.path, driver=driver, layer=folder, **kwargs
            )
            if chunk.shape[0] + sum_chunks < chunksize:
                # El fragmento será más pequeño que el chunksize, seguir agregando.
                layer_list.append(chunk)
                sum_chunks += chunk.shape[0]
            elif chunk.shape[0] + sum_chunks == chunksize:
                # El tamaño del fragmento será igual al chunksize, devolver el fragmento y reiniciar.
                layer_list.append(chunk)
                yield geopandas.GeoDataFrame(
                    pandas.concat(
                        layer_list,
                        ignore_index=True,
                    ),
                )
                layer_list = []
                sum_chunks = 0
            else:
                # El fragmento será más grande que el chunksize...
                while chunk.shape[0] + sum_chunks > chunksize:
                    # Comenzar a agregar fragmentos hasta alcanzar el chunksize.
                    slice_rows = chunksize - sum_chunks
                    slice_chunk = chunk.iloc[range(slice_rows)]
                    layer_list.append(slice_chunk)
                    yield geopandas.GeoDataFrame(
                        pandas.concat(
                            layer_list,
                            ignore_index=True,
                        ),
                    )
                    layer_list = []
                    sum_chunks = 0
                    chunk = chunk.iloc[range(slice_rows, chunk.shape[0])]
                # Finalmente, agregar el fragmento restante al siguiente chunk.
                layer_list.append(chunk)
                sum_chunks += chunk.shape[0]
        yield geopandas.GeoDataFrame(
            pandas.concat(
                layer_list,
                ignore_index=True,
            ),
        )

    def handle_linear_rings(
        self, errors: Literal["fail", "drop", "replace"] = "replace"
    ):
        """
        Maneja los anillos lineales (LinearRings) en el archivo KML.

        Args:
                errors (Literal["fail", "drop", "replace"]): La acción a realizar cuando se encuentren
                        errores en los anillos lineales.
                        - "fail": Lanza una excepción y falla si se encuentran errores.
                        - "drop": Elimina los anillos lineales con errores.
                        - "replace": Reemplaza las coordenadas faltantes en los anillos lineales con errores.

        """
        if errors == "fail":
            return
        with open(self.path, "r") as original_file:
            xml_data = original_file.read()
        soup = BeautifulSoup(xml_data, "xml")
        for linear_ring in soup.find_all("LinearRing"):
            coordinates = linear_ring.coordinates.string.split()
            if len(coordinates) < 1 and errors in ["drop", "replace"]:
                linear_ring.extract()
                continue
            if len(coordinates) < 4:
                if errors == "replace":
                    coordinates = coordinates + [
                        coordinates[-1] for _ in range(4 - len(coordinates))
                    ]
                    linear_ring.coordinates.string = " ".join(coordinates)
                    continue
                if errors == "drop":
                    linear_ring.extract()
                    continue
        self.set(path=os.path.join(self.temp_dir, "handle_linear_rings.kml"))
        with open(self.path, "w") as parsed_file:
            parsed_file.write(str(soup))
