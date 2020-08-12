FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN mkdir -p /usr/src/epcis
WORKDIR /usr/src/epcis

# run this like 
# docker run -v `pwd`:/usr/src/epcis epcis-hash -b my-events.json

COPY . /usr/src/app/
ENTRYPOINT [ "python", "/usr/src/app/epcis_event_hash_generator/main.py" ]
CMD ["-h"]