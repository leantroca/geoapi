from api.celery import app

from .core import (
    delete_layer,
    get_log,
    keep_track,
    kml_to_append_layer,
    kml_to_create_layer,
    temp_remove,
)


@app.task(bind=True)
def task_kml_to_create_layer(*args, **kwargs):
    """TBD"""
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    kml_to_create_layer(*args, **kwargs)
    temp_remove(kwargs["file"])
    print(f"{get_log(kwargs['log']).status=}")
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True)
def task_kml_to_append_layer(*args, **kwargs):
    """TBD"""
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    kml_to_append_layer(*args, **kwargs)
    temp_remove(kwargs["file"])
    print(f"{get_log(kwargs['log']).status=}")
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)


@app.task(bind=True)
def task_delete_layer(*args, **kwargs):
    """TBD"""
    keep_track(log=kwargs["log"], message="Processing.", status=205)
    delete_layer(*args, **kwargs)
    print(f"{get_log(kwargs['log']).status=}")
    if get_log(kwargs["log"]).status == 205:
        keep_track(log=kwargs["log"], append_message="Success!", status=210)
