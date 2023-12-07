FROM python:3.8-alpine

LABEL org.opencontainers.image.source=https://github.com/RalphTro/epcis-event-hash-generator
LABEL org.opencontainers.image.description="This container hosts web services for generating event hash. Basically supports `GET /health` and `POST /hash` http endpoints."

RUN apk --no-cache --update add bash inotify-tools curl

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 5000/tcp

COPY . /usr/src/app/
ENTRYPOINT ["python3", "/usr/src/app/webapi/api.py"]
