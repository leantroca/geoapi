import os
import tempfile
from typing import Union

import fiona
import geopandas
import pandas
from werkzeug.datastructures import FileStorage

fiona.drvsupport.supported_drivers["KML"] = "rw"
fiona.drvsupport.supported_drivers["LIBKML"] = "rw"


def read_kml(
    data: Union[str, FileStorage], chunksize: int = None, **kwargs
) -> geopandas.GeoDataFrame:
    # Reads from local filesystem.
    if isinstance(data, str):
        if chunksize:
            for chunk in load_kml(path=data, chunksize=chunksize, **kwargs):
                yield chunk
        else:
            return load_kml(path=data, **kwargs)
    # Saves into temporary file and reads from local filesystem.
    if isinstance(data, FileStorage):
        if chunksize:
            for chunk in load_filestorage_kml(data=data, chunksize=chunksize, **kwargs):
                yield chunk
        else:
            return load_filestorage_kml(data=data, **kwargs)


def load_filestorage_kml(data: FileStorage, chunksize: int = None, **kwargs) -> str:
    with tempfile.TemporaryDirectory() as tempdir:
        tempstorage = os.path.join(tempdir, "temp.kml")
        data.save(tempstorage)
        if chunksize:
            for chunk in load_kml(path=tempstorage, chunksize=chunksize, **kwargs):
                yield chunk
        else:
            return load_kml(path=tempstorage, **kwargs)


def load_kml(path: str, chunksize: int = None, **kwargs) -> geopandas.GeoDataFrame:
    if chunksize:
        return load_kml_in_chunks(path=path, chunksize=chunksize, **kwargs)
    folders = fiona.listlayers(path)
    load_kml = geopandas.GeoDataFrame(
        pandas.concat(
            (
                geopandas.read_file(path, dirver="KML", layer=folder, **kwargs)
                for folder in folders
            ),
            ignore_index=True,
        ),
    )
    return load_kml


def load_kml_in_chunks(path: str, chunksize=50, **kwargs) -> geopandas.GeoDataFrame:
    folders = fiona.listlayers(path)
    layer_list = []
    sum_chunks = 0
    for i, folder in enumerate(folders):
        chunk = geopandas.read_file(path, dirver="KML", layer=folder, **kwargs)
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
            # Chunk will be nigger than chunksize...
            while chunk.shape[0] + sum_chunks > chunksize:
                # Start adding silces until reaching chunksize.
                slice_rows = chunksize - sum_chunks
                slice_chunk = chunk.iloc[range(slice_rows)]
                layer_list.append(slice_chunk)
                yield geopandas.GeoDataFrame(
                    pandas.concat(
                        layer_list,
                        ignore_index=True,
                    ),
                )
                layer_list = []  # [chunk.loc[range(slice_rows, chunk.shape[0])]]
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


def clean_xml(df: geopandas.GeoDataFrame):
    for column in df.columns:
        if column in ["geometry"]:
            continue
        for row in df[column]:
            if "<br>" in row:
                print(
                    {
                        field.split(":")[0].strip(): field.split(":")[1].strip()
                        for field in row.split("<br>")
                    }
                )
