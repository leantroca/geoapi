from celery import Celery

from utils.postgis_interface import PostGIS

postgis = PostGIS()

app = Celery("api")

app.config_from_object("api.celeryconfig")
