from celery import Celery

app = Celery("api")

app.config_from_object("api.celeryconfig")
