# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to not create a virtual environment. 
# This makes it install dependencies into the system's python path,
# which is a common and clean practice for Docker containers.
RUN poetry config virtualenvs.create false

# Copy only the dependency definition files
COPY pyproject.toml poetry.lock ./

# Install production dependencies using poetry's native command
# --no-dev: Skips development dependencies
# --no-root: Skips installing the project package itself
# --no-interaction --no-ansi: For cleaner logs
RUN poetry install --no-dev --no-root --no-interaction --no-ansi

# Copy the rest of the local code to the container image.
COPY . .

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Run the web server on container startup.
# Gunicorn is now available in the system's PATH.
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 main:app
