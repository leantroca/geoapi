FROM "docker.osgeo.org/geoserver:2.23.1"

WORKDIR /geoserver

ENV SKIP_DEMO_DATA="true"
ENV ROOT_WEBAPP_REDIRECT="true"
ENV INSTALL_EXTENSIONS="true"
ENV STABLE_EXTENSIONS="importer"
ENV CORS_ENABLED="true"

ADD ./src/etc/sld /home/styles

COPY ./docker/geoserver/workspace-setup.sh /geoserver/workspace-setup.sh
RUN chmod +x /geoserver/workspace-setup.sh
RUN sh /geoserver/workspace-setup.sh

ADD ./src/etc/png /opt/geoserver_data/workspaces/geoapi/styles/png

CMD ["startup.sh"]