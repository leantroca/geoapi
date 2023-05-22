# Documentación de GeoAPI

Este repositorio contiene una API construida con Flask y Flask-RESTX. Utiliza SQLAlchemy para conectarse a una base de datos PostGIS y Alembic para las migraciones de la base de datos. La API está diseñada para ingestar archivos KML en la base de datos, ya sea mediante la carga de archivos o URLs HTTP. Además, se integra con un GeoServer para importar las geometrías desde la base de datos y hacerlas disponibles para su uso público con el estándar de Servicio de Mapas Web (WMS).

## Tabla de contenidos

*   [Comenzando](#comenzando)
*   [Instalación](#instalación)
*   [Configuración](#configuración)
*   [Ejecución de la API](#ejecución-de-la-api)
*   [Endpoints de la API](#endpoints-de-la-api)
*   [Ingestión de datos](#ingestión-de-datos)
*   [Migraciones de la base de datos](#migraciones-de-la-base-de-datos)
*   [Integración con GeoServer](#integración-con-geoserver)
*   [Contribuciones](#contribuciones)
*   [Licencia](#licencia)

## Comenzando

Para comenzar con la API, sigue las instrucciones a continuación.

### Instalación

1. Clona este repositorio en tu máquina local:

```git clone https://github.com/leantroca/geoapi.git```

2. Ingresa al directorio del proyecto:

```cd geoapi```

3. Instala Poetry (si aún no está instalado):

```curl -sSL https://install.python-poetry.org | python3 -```

4. Instala las dependencias del proyecto utilizando Poetry:

```poetry install```

5. Activa el entorno virtual del proyecto:

```poetry shell```

### Configuración

Antes de ejecutar la API, debes configurar los ajustes necesarios. Escribe el archivo `etc/settings.toml` ubicado en el directorio `etc` del proyecto con las configuraciones deseadas. Un archivo de ejemplo se encuentra en `etc/settings.example.toml`. Es posible que debas establecer los siguientes parámetros:

* **Configuración del servidor GeoAPI**: Establece los parámetros `BASE_URL`, `TIMEZONE`, `COORDINATE_SYSTEM` y `DEFAULT_CHUNKSIZE` para configurar el servidor GeoAPI según las necesidades y recursos de tu proyecto.

* **Configuración de la base de datos PostGIS**: Modifica los parámetros `POSTGIS_HOST`, `POSTGIS_USER`, `POSTGIS_PASS`, `POSTGIS_DATABASE`, `POSTGIS_SCHEMA` y `POSTGIS_DRIVER` para especificar los detalles de conexión de tu base de datos PostGIS.

* **Configuración de GeoServer**: Ajusta los parámetros `GEOSERVER_BASE_URL`, `GEOSERVER_USERNAME`, `GEOSERVER_PASSWORD`, `GEOSERVER_WORKSPACE` y `GEOSERVER_DATASTORE` para que coincidan con tu instancia de GeoServer.

## Migraciones de la base de datos

Para administrar los cambios en el esquema de la base de datos, este proyecto utiliza Alembic para las migraciones. Sigue los siguientes pasos para autogenerar las migraciones y actualizar la base de datos:

1. Genera un script de migración inicial:

```poetry run alembic revision --autogenerate -m "Migración inicial"```

2. Revisa el script de migración generado en el directorio `models/alembic/versions`.

3. Actualiza la base de datos a la última versión:

```alembic upgrade head```

4. Repite los pasos 1-3 cada vez que realices cambios en el esquema de la base de datos.

### Ejecución de la API

Para ejecutar la API, ejecuta el siguiente comando:

```flask --app app run```

La API comenzará a ejecutarse en `http://localhost:5000`.

## Ingestión de datos

La API proporciona dos métodos para ingestar archivos KML en la base de datos:

1. **Carga de archivos**: Utiliza los endpoints `/geoserver/kml` para cargar un archivo KML como un campo de datos de formulario llamado `file`.

2. **URL HTTP**: Utiliza los endpoints `/geoserver/url` para ingestar un archivo KML desde una URL HTTP dada.

## Endpoints de la API

Los siguientes endpoints están disponibles en la API:

### Namespace de Estado
* `/status/layers`: Lista las capas disponibles en el espacio de trabajo de GeoServer.
* `/status/batch/<int:id>`: Solicita el estado de un lote de geometrías previamente cargado.

### Namespace de GeoServer
* `/geoserver/kml/form/create`: Crea una capa de GeoServer a partir de un archivo KML proporcionado.
* `/geoserver/kml/form/append`: Agrega a una capa de GeoServer desde un archivo KML proporcionado.
* `/geoserver/url/form/create`: Crea una capa de GeoServer a partir de una URL HTTP proporcionada.
* `/geoserver/url/form/append`: Agrega a una capa de GeoServer desde una URL HTTP proporcionada.
* `/geoserver/layer/form/delete`: Elimina una capa de GeoServer y sus geometrías.

Consulta la documentación de la API para obtener información detallada sobre cada endpoint.

## Integración con GeoServer

Para importar las geometrías desde la base de datos a un GeoServer y hacerlas disponibles a través del estándar de Servicio de Mapas Web (WMS), sigue estos pasos:

1. Configura una instancia de GeoServer.

2. Actualiza los parámetros de configuración de GeoServer en `etc/settings.toml` (consulta la sección [Configuración](#configuración)).

3. Ejecuta los endpoints `/geoserver/kml` y `/geoserver/url` de tipo `POST` y `PUT` para importar las geometrías en las capas de GeoServer.

4. Las geometrías importadas deberían ser accesibles en el `workspace` y `datastore` especificados a través del servicio WMS proporcionado por GeoServer.

## Contribuciones

Se aceptan contribuciones a esta API. Si encuentras algún problema o deseas proponer mejoras, envía una solicitud de extracción o abre un problema en el repositorio de GitHub.
