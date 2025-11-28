#!/bin/sh

echo -n "$A1CTF_FLAG" > /flag
unset A1CTF_FLAG

export USERNAME="admin"
export PASSWORD="$(head -c 16 /dev/random | xxd -p)"

uvicorn main:app --host 0.0.0.0 --port 8000
