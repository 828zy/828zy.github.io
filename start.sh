#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/build.py
echo 'Local preview: http://127.0.0.1:4000'
exec python3 -m http.server 4000 --bind 127.0.0.1
