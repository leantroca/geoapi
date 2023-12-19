from utils.config import settings

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

broker_url = settings.CELERY_BROKER
broker_transport_options = {"visibility_timeout": 3600 * 6}

imports = (
    "api.geoserver.tasks",
    "api.postgis.tasks",
)
