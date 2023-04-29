import fiona
import geopandas
import pandas
import re

fiona.drvsupport.supported_drivers["KML"] = "rw"

def df(path:str) -> geopandas.GeoDataFrame:
	folders = fiona.listlayers(path)
	df = geopandas.GeoDataFrame(
		pandas.concat(
			(geopandas.read_file(path, dirver="KML", folder=folder) for folder in folders),
			ignore_index=True,
		),
	)
	clean_xml(df)
	return df


def clean_xml(df:geopandas.GeoDataFrame):
	for column in df.columns:
		if column in ["geometry"]:
			continue
		for row in df[column]:
			if "<br>" in row:
				print({field.split(":")[0].strip(): field.split(":")[1].strip() for field in  a.split("<br>")})

