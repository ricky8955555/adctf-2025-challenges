#!/bin/sh

sed -i 's_flag{}_'"$A1CTF_FLAG"'_' config.yml
unset A1CTF_FLAG

pdm run uvicorn nekoqa.application:app --host 0.0.0.0 --port 8000
