#!/bin/bash

source /home/settings.toml

sh /opt/startup.sh &

echo "Waiting for Geoserver to deploy..."
until curl -sSf http://localhost:8080/geoserver > /dev/null
do
   sleep 2
done

curl -s -X POST http://localhost:8080/geoserver/rest/workspaces?default=true -u $GEOSERVER_USERNAME:$GEOSERVER_PASSWORD -H  "accept: text/html" -H  "content-type: application/json" -d '{"workspace": {"name": "'$GEOSERVER_WORKSPACE'"}}'

curl -s -X POST http://localhost:8080/geoserver/rest/workspaces/$GEOSERVER_WORKSPACE/datastores -u $GEOSERVER_USERNAME:$GEOSERVER_PASSWORD -H  "accept: application/xml" -H  "content-type: application/json" -d '{"dataStore": {"name": "postgis", "connectionParameters": {"entry": [{"@key":"host","$":"'$POSTGIS_HOSTNAME'"}, {"@key":"port","$":"'$POSTGIS_PORT'"}, {"@key":"database","$":"'$POSTGIS_DATABASE'"}, {"@key":"schema","$":"'$POSTGIS_SCHEMA'"}, {"@key":"user","$":"'$POSTGIS_USER'"}, {"@key":"passwd","$":"'$POSTGIS_PASS'"}, {"@key":"dbtype","$":"postgis"}]}}}'

# Iterate through each file in the folder
folder_path="/home/styles"
for file in "$folder_path"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        filename="${filename%.*}"
        echo "Pushing style $filename"
        curl -s -X POST http://localhost:8080/geoserver/rest/workspaces/$GEOSERVER_WORKSPACE/styles?name=$filename -u $GEOSERVER_USERNAME:$GEOSERVER_PASSWORD -d @$file -H "Content-type: application/vnd.ogc.sld+xml"
        sleep 1
    fi
done
# Copy png files expected by styles
cp -r $folder_path/png $GEOSERVER_STYLE_STORAGE/
