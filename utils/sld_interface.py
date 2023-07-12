from typing import Type, Union
from werkzeug.datastructures import FileStorage
import re
import os
import tempfile
import requests


class SLD:
    """Interfaz para archivos SLD."""

    def __init__(
        self,
        data: Union[str, FileStorage, Type["SLD"]],
        **kwargs,
    ):
        """TBD"""
        if isinstance(data, str):
            if re.match(r"^(http|https)://", data.strip().lower()):
                self._path = self.temp_handle
                response = requests.get(data)
                response.raise_for_status()
                with open(self._path, "wb") as writer:
                    writer.write(response.content)
                return
            self._temp_dir = None
            self._path = data
            return
        if isinstance(data, FileStorage):
            self._path = self.temp_handle
            data.save(self._path)
            return
        if self.isselfinstance(data):
            self._temp_dir = None
            self._path = data.path
            return
        raise Exception(f"data {data} of class {type(data)} can't be handled.")

    def __del__(self):
        """
        Libera los recursos utilizados por el objeto KML.

        """
        if self._temp_dir is not None:
            self._temp_dir.cleanup()

    @classmethod
    def isselfinstance(cls, obj) -> bool:
        return isinstance(obj, cls)

    @property
    def temp_dir(self) -> str:
        """
        Directorio temporal utilizado para almacenar los archivos KML.

        Returns:
                str: Ruta del directorio temporal.

        """
        if getattr(self, "_temp_dir", None) is None:
            self._temp_dir = tempfile.TemporaryDirectory()
        return self._temp_dir.name

    @property
    def temp_handle(self) -> str:
        """TBD"""
        return os.path.join(self.temp_dir, "handle.sld")

    @property
    def path(self) -> str:
        """
        Ruta del archivo KML.

        Returns:
                str: Ruta del archivo KML.

        """
        return self._path

    def read(self):
        """TBD"""
        return open(self._path, "rb")