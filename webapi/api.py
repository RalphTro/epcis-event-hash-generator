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

    from epcis_event_hash_generator import hash_generator

    if request.content_type == 'application/json':
        (hashes, prehashes) = hash_generator.epcis_hash_from_json(request.data)
        return ",".join(hashes)
    elif request.content_type == 'application/xml':
        (hashes, prehashes) = hash_generator.epcis_hash_from_xml(request.data)
        return ",".join(hashes)
    else:
        return abort(404, "Invalid content_type in request")


app.run(host='0.0.0.0')
