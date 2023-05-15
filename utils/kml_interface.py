import os
import tempfile
from typing import Union, Optional

import fiona
import geopandas
import pandas
from werkzeug.datastructures import FileStorage
from etc.config import settings


class KML():
    """KML file handler."""
    fiona.drvsupport.supported_drivers["KML"] = "rw"
    fiona.drvsupport.supported_drivers["LIBKML"] = "rw"

    def __init__(
        self,
        file:Union[str, FileStorage],
        driver:Optional[str]="KML",
        chunksize:Optional[int]=None,
        optional:Optional[dict]={},
        **kwargs,
    ):
        self._driver = driver
        self._chunksize = chunksize # or getattr(settings, "DEFAULT_CHUNKSIZE", None)
        optional.update(kwargs)
        self._optional = optional
        if isinstance(file, str):
            self._temp_dir = None
            self._path = file
            return
        if isinstance(file, FileStorage):
            self._temp_dir = tempfile.TemporaryDirectory()
            self._path = os.path.join(self._temp_dir.name, "handle.kml")
            file.save(self._path)
            return
        raise Exception(f"file {file} of class {type(file)} can't be handled.")

    def __del__(self):
        self._temp_dir.cleanup()

    @property
    def path(self) -> str:
        return self._path

    @property
    def driver(self) -> str:
        return self._driver

    @property
    def chunksize(self) -> int:
        return self._chunksize

    @property
    def optional(self) -> dict:
        return self._optional

    @property
    def folders(self) -> list[str]:
        return fiona.listlayers(self.path)

    def set(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

    def read_kml(
        self, driver:Optional[str]=None, chunksize: Optional[int] = None, **kwargs
    ) -> geopandas.GeoDataFrame:
        driver = driver or self.driver
        chunksize = chunksize if chunksize is not None else self.chunksize
        optional = self.optional.copy()
        optional.update(kwargs)
        if chunksize:
            for chunk in self.load_kml_in_chunks(chunksize=chunksize, **optional):
                yield chunk
        else:
            return self.load_kml(**optional)

    def load_kml(self, driver:Optional[str] = None, **kwargs) -> geopandas.GeoDataFrame:
        driver = driver or self.driver
        optional = self.optional.copy()
        optional.update(kwargs)
        load_kml = geopandas.GeoDataFrame(
            pandas.concat(
                (
                    geopandas.read_file(path, driver=driver, layer=folder, **optional)
                    for folder in self.folders
                ),
                ignore_index=True,
            ),
        )
        return load_kml

    def load_kml_in_chunks(self, driver:Optional[str] = None, chunksize:Optional[int]=None, **kwargs) -> geopandas.GeoDataFrame:
        driver = driver or self.driver
        chunksize = chunksize or self.chunksize
        layer_list = []
        sum_chunks = 0
        for i, folder in enumerate(self.folders):
            chunk = geopandas.read_file(self.path, driver=driver, layer=folder, **kwargs)
            if chunk.shape[0] + sum_chunks < chunksize:
                # Chunk will be smaller than chunksize, continue appending.
                layer_list.append(chunk)
                sum_chunks += chunk.shape[0]
            elif chunk.shape[0] + sum_chunks == chunksize:
                # Chunk size will be chunksize, yield chunk and restart.
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
                # Chunk will be bigger than chunksize...
                while chunk.shape[0] + sum_chunks > chunksize:
                    # Start adding slices until reaching chunksize.
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
                # Finally, add remaining slice to the next chunk.
                layer_list.append(chunk)
                sum_chunks += chunk.shape[0]
        yield geopandas.GeoDataFrame(
            pandas.concat(
                layer_list,
                ignore_index=True,
            ),
        )