#!/bin/sh
# Prepare the database on /data, then start the application as the user cdpp.
# A new volume is owned by root, so this script starts as root.
set -eu

as_cdpp() {
    setpriv --reuid=cdpp --regid=cdpp --clear-groups "$@"
}

chown -R cdpp:cdpp /data
if [ -s /data/cdpp.sqlite3 ]; then
    as_cdpp cdpp db upgrade
else
    as_cdpp cdpp load-data
fi

exec setpriv --reuid=cdpp --regid=cdpp --clear-groups \
    gunicorn --bind 0.0.0.0:8000 --workers 3 --no-control-socket "cdpp:create_app()"
