FROM python:3.8-alpine3.10

ARG VER_PYTHON="3.8"

RUN apk add --no-cache \
        bash \
        curl \
        vim \
        postgresql-client \
        postgresql-dev \
        python3 \
    && python3 --version \
    && python3 -c "import os, sys;assert sys.version.startswith(os.environ.get('VER_PYTHON'))" \
    && pip3 --version

WORKDIR /repo

COPY Pipfile /repo/Pipfile
COPY Pipfile.lock /repo/Pipfile.lock

RUN apk add --no-cache \
        gcc \
        musl-dev \
        python3-dev

RUN pip3 install pipenv \
    && pipenv install --dev --system --deploy

COPY ./ /repo/

ENV PYTHONPATH=/repo

RUN ["chmod", "+x", "/repo/files/wait-for-it.sh"]
RUN ["chmod", "+x", "/repo/files/app-init.sh"]

ENTRYPOINT /repo/files/app-init.sh