#!/bin/sh

set -o errexit -o xtrace

echo "Waiting for db..."
/repo/files/wait-for-it.sh -t 10 $POSTGRES_HOST:$POSTGRES_PORT

psql postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT \
  -c "CREATE DATABASE $POSTGRES_DB" || true

cd /repo
alembic upgrade 782e29ef841d
