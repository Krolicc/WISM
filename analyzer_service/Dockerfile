# 1. Use an official Python runtime as a parent image
FROM python:3.11

# 2. Set the working directory in the container
WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

# 3. Install Poetry
RUN pip install poetry

# 4. Copy only the dependency file to leverage Docker layer caching
COPY pyproject.toml ./

# 5. Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# 6. Copy the rest of the application's source code from your host to your image filesystem.
COPY . .

# The command to run the application will be provided by docker-compose
