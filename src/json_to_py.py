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


SKIP_KEYS = ["isA"]

def json_to_py(json_obj):
    """ Recursively convert a string/list/dict to a simple python object
    """
    
    py_obj = ("", "", [])

    if isinstance(json_obj, list):
        for child in json_obj:
            py_obj[2].append(json_to_py(child))
    elif isinstance(json_obj, dict):
        if "isA" in json_obj:
            py_obj = (json_obj["isA"], "", [])
            
        for (key, val) in [x for x in json_obj.items() if x[0] not in SKIP_KEYS]:
            child = json_to_py(val)
            child = (key, child[1], child[2])

            # Names of list elements (e.g. 'epc' elements of 'epsList') are omitted in current json ld form -> restore
            if key.endswith("List"):
                named_elements=[]
                for element in child[2]:
                    if not element[0]:
                        named_elements.append((key[:-4], element[1], element[2]))
                    else:
                        named_elements.append(element)
                child = (child[0], child[1], named_elements)
            
            py_obj[2].append(child)
    else:
        logging.debug("converting '%s' to str", json_obj)
        return ("",str(json_obj),[])
    
    py_obj[2].sort()
    return py_obj


def event_list_from_epcis_document_json(path):
    """Read EPCIS JSON document and generate the event List in the form of a simple python object

    """
    with open(path, 'r') as file:
        data = file.read()

    json_obj = json.loads(data)

    event_list = json_obj["epcisBody"]["eventList"]
    events=[]

    for event in event_list:
        events.append(json_to_py(event))
    
    return ("eventList", "", events)
