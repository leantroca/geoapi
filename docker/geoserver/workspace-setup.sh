#!/bin/sh

sh /opt/startup.sh &

echo "Waiting for Geoserver to deploy..."
until curl -sSf http://localhost:8080/geoserver > /dev/null
do
   sleep 2
done

curl -s -X POST http://localhost:8080/geoserver/rest/workspaces?default=true -u admin:geoserver -H  "accept: text/html" -H  "content-type: application/json" -d '{"workspace": {"name": "geoapi"}}'

curl -s -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/datastores -u admin:geoserver -H  "accept: application/xml" -H  "content-type: application/json" -d '{"dataStore": {"name": "postgis", "connectionParameters": {"entry": [{"@key":"host","$":"postgis"}, {"@key":"port","$":"5432"}, {"@key":"database","$":"geoserver"}, {"@key":"schema","$":"geoapi"}, {"@key":"user","$":"geoserver"}, {"@key":"passwd","$":"geoserver"}, {"@key":"dbtype","$":"postgis"}]}}}'

curl -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/styles?name=estilo-base-rojo -u admin:geoserver -d @/home/styles/estilo-base-rojo.sld -H "Content-type: application/vnd.ogc.sld+xml"
curl -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/styles?name=estilo-base-azul -u admin:geoserver -d @/home/styles/estilo-base-azul.sld -H "Content-type: application/vnd.ogc.sld+xml"
curl -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/styles?name=estilo-base-verde -u admin:geoserver -d @/home/styles/estilo-base-verde.sld -H "Content-type: application/vnd.ogc.sld+xml"
curl -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/styles?name=estilo-base-amarillo -u admin:geoserver -d @/home/styles/estilo-base-amarillo.sld -H "Content-type: application/vnd.ogc.sld+xml"
curl -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/styles?name=estilo-base-violeta -u admin:geoserver -d @/home/styles/estilo-base-violeta.sld -H "Content-type: application/vnd.ogc.sld+xml"
curl -X POST http://localhost:8080/geoserver/rest/workspaces/geoapi/styles?name=estilo-base-blanco -u admin:geoserver -d @/home/styles/estilo-base-blanco.sld -H "Content-type: application/vnd.ogc.sld+xml"