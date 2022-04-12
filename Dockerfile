FROM python:3.8-alpine

RUN apk --no-cache --update add bash inotify-tools curl

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 5000/tcp

COPY . /usr/src/app/
ENTRYPOINT ["python3", "/usr/src/app/webapi/api.py"]
