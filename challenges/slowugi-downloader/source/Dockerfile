FROM python:3.12-alpine

WORKDIR /app

COPY app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app/ .
COPY start.sh /start.sh

EXPOSE 8000

ENTRYPOINT [ "/bin/sh", "/start.sh" ]
