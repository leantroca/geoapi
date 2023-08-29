FROM geoapi-poetry-env

WORKDIR /geoapi

# Expose the API port
EXPOSE 5000

COPY ./docker/geoapi/startup.sh /geoapi/startup.sh
RUN chmod +x /geoapi/startup.sh

# Start the API
CMD ["/geoapi/startup.sh"]
