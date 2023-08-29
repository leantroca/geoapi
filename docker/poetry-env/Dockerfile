# Use a Python base image
FROM python:3.9

# Set the working directory
WORKDIR /geoapi

# Install utilities
RUN apt-get update && apt-get install -y postgresql-client

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/share/pypoetry/venv/bin:$PATH"

# Copy project description
COPY ./pyproject.toml /geoapi
COPY ./poetry.lock /geoapi

# Install API dependencies using Poetry
RUN poetry install
