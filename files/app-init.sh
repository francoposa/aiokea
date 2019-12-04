#!/bin/sh

set -o errexit -o xtrace

echo "Initializing db..."
/bin/sh /repo/files/db-init.sh

echo "***************Starting aiohttp-postgres service...***************"

cd /repo
exec python -m app -c config.docker.json