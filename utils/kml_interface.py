import fiona
import geopandas
import pandas

fiona.drvsupport.supported_drivers["KML"] = "rw"
fiona.drvsupport.supported_drivers["LIBKML"] = "rw"


def read_kml(path: str, chunksize: int = None, **kwargs) -> geopandas.GeoDataFrame:
    if chunksize:
        return read_kml_in_chunks(path, chunksize, **kwargs)
    folders = fiona.listlayers(path)
    read_kml = geopandas.GeoDataFrame(
        pandas.concat(
            (
                geopandas.read_file(path, dirver="KML", folder=folder, **kwargs)
                for folder in folders
            ),
            ignore_index=True,
        ),
    )
    return read_kml


def read_kml_in_chunks(path: str, chunksize=50, **kwargs) -> geopandas.GeoDataFrame:
    folders = fiona.listlayers(path)
    layer_list = []
    sum_chunks = 0
    for i, folder in enumerate(folders):
        chunk = geopandas.read_file(path, dirver="KML", layer=folder, **kwargs)
        if chunk.shape[0] + sum_chunks < chunksize:
            layer_list.append(chunk)
            sum_chunks += chunk.shape[0]
        elif chunk.shape[0] + sum_chunks == chunksize:
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
            while chunk.shape[0] + sum_chunks > chunksize:
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
