FROM postgis/postgis:15-master

ENV POSTGRES_DB="geoserver"
ENV POSTGRES_USER="geoserver"
ENV POSTGRES_PASSWORD="geoserver"

COPY ./docker/postgis/CreateDB.sql /docker-entrypoint-initdb.d/CreateDB.sql
RUN chmod a+r /docker-entrypoint-initdb.d/*

