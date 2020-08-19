FROM python:3.8-alpine

RUN apk --no-cache --update add bash inotify-tools curl

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN mkdir -p /events
WORKDIR /events
VOLUME [ "/events" ]
# run this like 
# docker run -v `pwd`:/events epcis-hash 
# to start whatching the current folder for json/xml files for hashing

COPY . /usr/src/app/
ENTRYPOINT [ "/usr/src/app/auto-hash-folder.sh", "/events", "/usr/src/app/epcis_event_hash_generator/" ]
