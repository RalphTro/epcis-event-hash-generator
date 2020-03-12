"""Convert an EventList contained in an EPCIS 2.0 document in JSON LD format into a simple python object.

See the description of xml_to_py for more details about what 'simple' means here.

For example
{
  "isA": "ObjectEvent",
  "eventTime": "2019-04-02T15:00:00+01:00",
  "eventTimeZoneOffset": "+01:00",
  "epcList": [
    "urn:epc:id:sgtin:4012345.011111.9876",
"urn:epc:id:sgtin:4012345.011111.5432"
  ],
  "action": "OBSERVE",
}

is converted to

("ObjectEvent","",[
  ("eventTime","2019-04-02T15:00:00+01:00", []),
  ("eventTimeZoneOffset","+01:00", []),
  ("epcList", "", [
    ("epc", "urn:epc:id:sgtin:4012345.011111.5432", []),
    ("epc", "urn:epc:id:sgtin:4012345.011111.9876", [])
  ],
  ("action", "OBSERVE", [])
])

The EPCIS standard is used to add missing names (such as "epc" in the above example) to be consistent with the XML version.


.. module:: json_to_py

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>, Sebastian Schmittner <schmittner@eecc.info>

Copyright 2020 Ralph Troeger, Sebastian Schmittner

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""

import logging
import json

def json_to_py(json_obj):
    py_obj = ("","",[])
    if "isA" in json_obj:
        py_obj[0] = json_obj["isA"]

    
    

def event_list_from_epcis_document_json(path):
    """Read EPCIS JSON document and generate the event List in the form of a simple python object

    """
    data = json.loads(path)

    event_list = data["epcisBody"]["eventList"]
    events=[]

    for event in event_list:
        events.append(json_to_py(event))
    
    return ("eventList","",events)

