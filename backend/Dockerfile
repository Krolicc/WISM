# Use an official Python image.
FROM python:3.11

# Set the working directory and tell Python to look for modules here
WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install poetry
RUN pip install poetry

# Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create a virtual environment and install dependencies.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Copy the rest of the application code to the container image.
COPY . .

# The command to run the application will be specified in the docker-compose.yml file
