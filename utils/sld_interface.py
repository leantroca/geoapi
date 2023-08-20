from typing import Type, Union
from werkzeug.datastructures import FileStorage
import re
import os
import tempfile
import requests
import io

class SLD:
    """
    Interfaz para archivos SLD.

    Esta clase proporciona una interfaz para manejar archivos SLD (Styled Layer Descriptor),
    ya sea a través de rutas de archivo, objetos FileStorage o instancias de la propia
    clase. Los archivos SLD se pueden leer y manipular utilizando esta interfaz.

    Args:
        data (Union[str, FileStorage, Type["SLD"]]): Los datos del archivo SLD, que pueden
            ser una ruta de archivo, un objeto FileStorage o una instancia de la clase SLD.
        **kwargs: Argumentos adicionales no utilizados en esta implementación.

    Note:
        - Si se proporciona una URL HTTP/HTTPS como `data`, el archivo SLD será descargado
          y almacenado temporalmente para su uso.
        - Si se proporciona un objeto FileStorage, se guardará en un archivo temporal para
          su uso.
        - Si se proporciona una instancia existente de la clase SLD, se utilizará su
          ruta de archivo.

    """

    def __init__(
        self,
        data: Union[str, FileStorage, Type["SLD"]],
        **kwargs,
    ):
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
        Libera los recursos utilizados por el objeto SLD.

        Esta función se llama automáticamente cuando el objeto SLD se elimina, y se
        encarga de liberar los recursos utilizados, como los archivos temporales.

        """
        if self._temp_dir is not None:
            self._temp_dir.cleanup()

    @classmethod
    def isselfinstance(cls, obj) -> bool:
        """
        Verifica si el objeto es una instancia de la clase SLD.

        Args:
            obj: El objeto a verificar.

        Returns:
            bool: True si el objeto es una instancia de la clase SLD, False de lo
            contrario.

        """
        return isinstance(obj, cls)

    @property
    def temp_dir(self) -> str:
        """
        Directorio temporal utilizado para almacenar los archivos SLD.

        Returns:
            str: Ruta del directorio temporal.

        """
        if getattr(self, "_temp_dir", None) is None:
            self._temp_dir = tempfile.TemporaryDirectory()
        return self._temp_dir.name

    @property
    def temp_handle(self) -> str:
        """
        Ruta completa al archivo temporal utilizado para almacenar el SLD.

        Returns:
            str: Ruta completa al archivo temporal utilizado para almacenar el SLD.

        """
        return os.path.join(self.temp_dir, "handle.sld")

    @property
    def path(self) -> str:
        """
        Ruta del archivo SLD.

        Returns:
            str: Ruta del archivo SLD.

        """
        return self._path

    def read(self) -> io.BufferedReader:
        """
        Lee el contenido del archivo SLD.

        Returns:
            BufferedReader: Un objeto BufferedReader que permite leer el contenido
            del archivo SLD.

        """
        return open(self._path, "rb")