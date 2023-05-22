# GeoAPI Documentation

This repository contains an API built with Flask and Flask-RESTX. It utilizes SQLAlchemy to connect to a PostGIS database and Alembic for database migrations. The API is designed to ingest KML files into the database, either through file uploads or HTTP URLs. Additionally, it integrates with a GeoServer to import the geometries from the database and make them available for public use with the Web Map Service (WMS) standard.

## Table of Contents

*   [Getting Started](#getting-started)
*   [Installation](#installation)
*   [Configuration](#configuration)
*   [Running the API](#running-the-api)
*   [API Endpoints](#api-endpoints)
*   [Data Ingestion](#data-ingestion)
*   [Database Migrations](#database-migrations)
*   [GeoServer Integration](#geoserver-integration)
*   [Contributing](#contributing)
*   [License](#license)

## Getting Started

To get started with the API, please follow the instructions below.

### Installation

1. Clone this repository to your local machine:

```git clone https://github.com/leantroca/geoapi.git```

2. Change into the project directory:

```cd geoapi```

3. Install Poetry (if not already installed):

```curl -sSL https://install.python-poetry.org | python3 -```

4. Install the project dependencies using Poetry:

```poetry install```

5. Activate project virtual environment:

```poetry shell```

### Configuration

Before running the API, you need to configure the necessary settings. Write the `etc/settings.toml` file located in the project's `etc` directory with your desired configurations. An example file can be found in `etc/settings.example.toml`. You may need to set the following parameters:

* **GeoAPI Server Configuration**: Set the `BASE_URL`, `TIMEZONE`, `COORDINATE_SYSTEM`, `DEFAULT_CHUNKSIZE` parameters to  configure the GeoAPI server to your project needs and resources.

* **PostGIS Database Configuration**: Modify the `POSTGIS_HOST`, `POSTGIS_USER`, `POSTGIS_PASS`, `POSTGIS_DATABASE`, `POSTGIS_SCHEMA` and `POSTGIS_DRIVER` parameters to specify the connection details for your PostGIS database.

* **GeoServer Configuration**: Adjust the `GEOSERVER_BASE_URL`, `GEOSERVER_USERNAME`, `GEOSERVER_PASSWORD`, `GEOSERVER_WORKSPACE` and `GEOSERVER_DATASTORE` parameters to match your GeoServer instance.

## Database Migrations

To manage database schema changes, this project uses Alembic for migrations. Follow the steps below to autogenerate migrations and upgrade the database:

1.  Generate an initial migration script:

```poetry run alembic revision --autogenerate -m "Initial migration"```

1.  Review the generated migration script in the `models/alembic/versions` directory.

2.  Upgrade the database to the latest version:

```alembic upgrade head```

1.  Repeat steps 1-3 whenever you make changes to the database schema.

### Running the API

To run the API, execute the following command:

```flask --app app run```

The API will start running on `http://localhost:5000`.

## Data Ingestion

The API provides two methods for ingesting KML files into the database:

1. **File Upload**: Use the `/geoserver/kml` endpoints to upload a KML file as a form data field named `file`.

2. **HTTP URL**: Use the `/geoserver/url` endpoints to ingest a KML file from a given HTTP URL.

## API Endpoints

The following endpoints are available in the API:

### Status Namespace
* `/status/layers`: List layers available in geoserver's workspace.
* `/status/batch/<int:id>`: Request the status of a previously pushed batch of geometries.

### Geoserver Namespace
* `/geoserver/kml/form/create`: Create a geoserver layer from a provided KML file.
* `/geoserver/kml/form/append`: Append to a geoserver layer from a provided KML file.
* `/geoserver/url/form/create`: Create a geoserver layer from a provided http URL.
* `/geoserver/url/form/append`: Append to a geoserver layer from a provided http URL.
* `/geoserver/layer/form/delete`: Delete a geoserver layer and it's geometries.

Please refer to the API documentation for detailed information on each endpoint.

## GeoServer Integration

To import the geometries from the database into a GeoServer and make them available through the WMS standard, follow these steps:

1.  Set up a GeoServer instance.

2.  Update the GeoServer configuration parameters in `etc/settings.toml` (refer to the [Configuration](#configuration) section).

3.  Run the `/geoserver/kml` and `/geoserver/url` `POST` and `PUT` endpoints to import the geometries into GeoServer layers.

4.  The imported geometries should now be accessible in the specified `workspace` and `datastore` through the WMS service provided by GeoServer.

## Contributing

Contributions to this API are welcome. If you find any issues or would like to propose enhancements, please submit a pull request or open an issue on the GitHub repository.
