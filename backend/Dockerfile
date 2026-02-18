# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the dependency files
COPY pyproject.toml poetry.lock ./

# Use Poetry to generate a requirements.txt file
# --without-hashes is often needed for compatibility with some pip versions
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install production dependencies from the generated requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the local code to the container image.
COPY . .

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Run the web server on container startup.
# Use gunicorn for production with multiple workers.
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 main:app
