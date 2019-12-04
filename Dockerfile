FROM python:3.8-alpine3.10

ARG VER_PYTHON="3.8"

RUN apk add --no-cache \
        python3 \
    && python3 --version \
    && python3 -c "import os, sys;assert sys.version.startswith(os.environ.get('VER_PYTHON'))" \
    && pip3 --version

WORKDIR /app

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock


RUN apk add --no-cache \
        gcc \
        musl-dev \
        postgresql-dev \
        python3-dev

RUN pip3 install pipenv \
    && pipenv install --dev --system --deploy