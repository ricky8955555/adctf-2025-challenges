FROM python:3.12-alpine

WORKDIR /app

RUN pip install --no-cache-dir pdm

COPY server/ .
RUN pdm install --prod -G report

COPY start.sh /start.sh

EXPOSE 8000

ENTRYPOINT [ "/bin/sh", "/start.sh" ]
