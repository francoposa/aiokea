#!/bin/sh

cd /repo

./files/db-init.sh

python -m pytest -p no:warnings tests/