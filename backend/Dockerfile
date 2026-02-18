# Use an official Python image.
# The full image includes build tools needed for compiling some packages.
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create a virtual environment and install dependencies.
# This is a robust practice for Docker containers.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Copy the rest of the application code to the container image.
COPY . .

# The ENTRYPOINT is a shell command that first runs database migrations
# and then starts the Uvicorn server.
# It correctly uses the $PORT environment variable provided by Render.
ENTRYPOINT ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"]
