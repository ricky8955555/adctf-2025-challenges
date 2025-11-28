#!/bin/sh

echo -n "$A1CTF_FLAG" > /flag
unset A1CTF_FLAG

uvicorn main:app --host 0.0.0.0 --port 8000
