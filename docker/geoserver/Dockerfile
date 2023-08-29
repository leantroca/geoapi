FROM "docker.osgeo.org/geoserver:2.23.1"

WORKDIR /geoserver

ENV SKIP_DEMO_DATA="true"
ENV ROOT_WEBAPP_REDIRECT="true"
ENV INSTALL_EXTENSIONS="true"
ENV STABLE_EXTENSIONS="importer"
ENV CORS_ENABLED="true"

ADD ./etc/styles /home/styles

COPY ./etc/settings.toml /home/settings.toml
COPY ./docker/geoserver/workspace-setup.sh /geoserver/workspace-setup.sh
RUN chmod +x /geoserver/workspace-setup.sh
RUN bash /geoserver/workspace-setup.sh
RUN rm /home/settings.toml

CMD ["startup.sh"]