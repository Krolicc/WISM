FROM python:3.11

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install poetry

COPY ./torch-2.11.0+cpu-cp311-cp311-manylinux_2_28_x86_64.whl .

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-root --only main -vvv

COPY . .