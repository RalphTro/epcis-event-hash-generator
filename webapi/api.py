import os
import sys
from flask import Flask, abort, request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Welcome to event hash generator</h1><p>Use POST /hash endpoint to generate hash of your event</p>"


@app.route('/health', methods=['GET'])
def health():
    return "IMOK"


@app.route('/hash', methods=['POST'])
def hash():

    from epcis_event_hash_generator import hash_generator, json_to_py, xml_to_py

    if request.content_type == 'application/json' or request.content_type == 'application/ld+json':
        events = json_to_py.event_list_from_epcis_document_str(request.data.decode("utf-8"))
    elif request.content_type == 'application/xml':
        events = xml_to_py.event_list_from_epcis_document_str(request.data.decode("utf-8"))
    else:
        return abort(404, "Invalid content_type in request")
    
    hashes = hash_generator.epcis_hashes_from_events(events)
    return ",".join(hashes)


app.run(host='0.0.0.0')
