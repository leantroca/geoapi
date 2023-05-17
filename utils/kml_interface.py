import os
import tempfile
from typing import Optional, Union

import fiona
import geopandas
import pandas
from werkzeug.datastructures import FileStorage


class KML:
    """KML file handler."""

    fiona.drvsupport.supported_drivers["KML"] = "rw"
    fiona.drvsupport.supported_drivers["LIBKML"] = "rw"

    def __init__(
        self,
        file: Union[str, FileStorage],
        driver: Optional[str] = "KML",
        chunksize: Optional[int] = None,
        optional: Optional[dict] = {},
        **kwargs,
    ):
        self._driver = driver
        self._chunksize = chunksize
        optional.update(kwargs)
        self._optional = optional
        self._df = None
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
        if self._temp_dir is not None:
            self._temp_dir.cleanup()

    @property
    def temp_dir(self):
        if self._temp_dir is None:
            self._temp_dir = tempfile.TemporaryDirectory()
        return self._temp_dir

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
        self, driver: Optional[str] = None, chunksize: Optional[int] = None, **kwargs
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

    def load_kml(
        self, driver: Optional[str] = None, **kwargs
    ) -> geopandas.GeoDataFrame:
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
    ) -> geopandas.GeoDataFrame:
        driver = driver or self.driver
        chunksize = chunksize or self.chunksize
        layer_list = []
        sum_chunks = 0
        for i, folder in enumerate(self.folders):
            chunk = geopandas.read_file(
                self.path, driver=driver, layer=folder, **kwargs
            )
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

""" 
# HANDLE LinearRings with less than 4 coordinates into LineStrings
#
from bs4 import BeautifulSoup

# Parse the XML file
with open('your_file.xml', 'r') as file:
    xml_data = file.read()

soup = BeautifulSoup(xml_data, 'xml')

# Find all LinearRing tags
linear_rings = soup.find_all('LinearRing')

# Modify LinearRing tags to LineString tags
for linear_ring in linear_rings:
    # Create a new LineString tag
    line_string = soup.new_tag('LineString')

    # Copy the coordinates from LinearRing to LineString
    coordinates = linear_ring.coordinates.string
    line_string.append(soup.new_tag('coordinates'))
    line_string.coordinates.string = coordinates

    # Replace LinearRing with LineString
    linear_ring.replace_with(line_string)

# Save the changes to a new XML file
with open('updated_file.xml', 'w') as file:
    file.write(str(soup))
"""

# https://archivo.minhabitat.gob.ar/archivos/kml/CP_CAT_sanfernandodvcat_bairesdelsur_222viv.kml
