FROM geoapi-poetry-env

WORKDIR /geoapi

COPY ./docker/celery/startup.sh /geoapi/startup.sh
RUN chmod +x /geoapi/startup.sh

# Start the API
CMD ["/geoapi/startup.sh"]
