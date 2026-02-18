# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
WORKDIR /app
COPY . .

# Install production dependencies.
# We use the --no-cache-dir option to reduce the image size
# And --no-interaction --no-ansi to make the output cleaner
RUN pip install --no-cache-dir -r requirements.txt

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Run the web server on container startup.
# Use gunicorn for production with multiple workers.
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 main:app
