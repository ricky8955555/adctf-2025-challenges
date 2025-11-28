FROM python:3.12-alpine

RUN apk add --update --no-cache socat

WORKDIR /app
COPY calc.py /app/calc.py

EXPOSE 1337

ENTRYPOINT ["socat", "tcp-l:1337,reuseaddr,fork", "exec:'python3 /app/calc.py'"]
