#!/bin/bash

cd /geoapi/src/

poetry run celery -A api worker --loglevel=INFO