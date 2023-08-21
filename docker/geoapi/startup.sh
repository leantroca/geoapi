#!/bin/sh

cd /geoapi/src/

# Wait for the PostgreSQL database to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgis -p 5432 -d geoserver
do
  sleep 1
done

poetry run alembic upgrade head

# Wait for the Geoserver to be ready
echo "Waiting for Geoserver to deploy..."
until curl -sSf http://geoserver:8080/geoserver > /dev/null
do
   sleep 2
done

poetry run python app.py
