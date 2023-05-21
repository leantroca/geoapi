from utils.postgis_interface import PostGIS

postgis = PostGIS()


def get_log_record(id: int):
    return postgis.get_log_record(id=id)
