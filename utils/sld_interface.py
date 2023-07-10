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
        file: Union[str, FileStorage, Type["SLD"]],
        **kwargs,
    ):
        """TBD"""
        if isinstance(file, str):
            if re.match(r"^(http|https)://", file.strip().lower()):
                self._path = self.temp_handle
                response = requests.get(file)
                response.raise_for_status()
                with open(self._path, "wb") as writer:
                    writer.write(response.content)
                return
            self._temp_dir = None
            self._path = file
            return
        if isinstance(file, FileStorage):
            self._path = self.temp_handle
            file.save(self._path)
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
