"""Convert an EventList contained in an EPCIS 2.0 document in JSON LD format into a simple python object
via the main method event_list_from_epcis_document_str.

See the description of xml_to_py for more details about what 'simple' means here.

For example
{
  "isA": "ObjectEvent",
  "eventTime": "2019-04-02T15:00:00.000+01:00",
  "eventTimeZoneOffset": "+01:00",
  "epcList": [
    "urn:epc:id:sgtin:4012345.011111.9876",
"urn:epc:id:sgtin:4012345.011111.5432"
  ],
  "action": "OBSERVE",
}

is converted to

("ObjectEvent","",[
  ("eventTime","2019-04-02T15:00:00.000+01:00", []),
  ("eventTimeZoneOffset","+01:00", []),
  ("epcList", "", [
    ("epc", "urn:epc:id:sgtin:4012345.011111.5432", []),
    ("epc", "urn:epc:id:sgtin:4012345.011111.9876", [])
  ],
  ("action", "OBSERVE", [])
])

This module contains the straight forward part of the JSON to Py conversion. The tricky part of adjusting the data
model to get the same as when parsing the XML equivalent is imported from he json_xml_model_mismatch_correction module.


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

import json
import logging

try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator import json_xml_model_mismatch_correction

_namespaces = {}  # global dictionary gathered during parsing


def _namespace_replace(key):
    """If the key contains a namespace (followed by ":"), replace it with
    the {naemspace_url} from the _namespaces dict.
    """
    splitted = key.split(":", 1)
    if len(splitted) > 1:
        return _namespaces[splitted[0]] + splitted[1]

    return key


def _collect_namespaces_from_jsonld_context(context):
    global _namespaces

    if not(isinstance(context, str)):
        if(isinstance(context, list)):
            for c in context:
                if not(isinstance(c, str)):
                    for key in c.keys():
                        _namespaces[key] = "{" + c[key] + "}"
        else:
            for key in c.keys():
                _namespaces[key] = "{" + c[key] + "}"


def _json_to_py(json_obj):
    """ Recursively convert a string/list/dict to a simple python object
    """
    global _namespaces

    py_obj = ("", "", [])

    if isinstance(json_obj, list):
        for child in json_obj:
            py_obj[2].append(_json_to_py(child))
    elif isinstance(json_obj, dict):
        if "isA" in json_obj:
            py_obj = (json_obj["isA"], "", [])

        if "#text" in json_obj:
            py_obj = (py_obj[0], json_obj["#text"], py_obj[2])

        to_be_ignored = ["isA", "#text", "rdfs:comment", "comment"]
        for (key, val) in [x for x in json_obj.items() if x[0] not in to_be_ignored]:
            if key.startswith("@xmlns"):
                _namespaces[key[7:]] = "{" + val + "}"
                logging.debug("Namespaces: %s", _namespaces)

                py_obj = (_namespace_replace(py_obj[0]), py_obj[1], py_obj[2])
            else:
                # first find namespaces in child, then replace in key!
                child = _json_to_py(val)

                key = _namespace_replace(key)

                if isinstance(val, list):
                    for element in child[2]:
                        py_obj[2].append((key, element[1], element[2]))
                else:
                    child = (key, child[1], child[2])
                    py_obj[2].append(child)

    else:
        logging.debug("converting '%s' to str", json_obj)
        return "", str(json_obj), []

    py_obj[2].sort()
    return py_obj


def event_list_from_epcis_document_str(data):
    """
    Parse the JSON str data and convert to a simple python object.
    Apply the format corrections to match what we get from the respective xml representation.
    """

    json_obj = json.loads(data)

    if not(json_obj.get("@context") is None):
        _collect_namespaces_from_jsonld_context(json_obj["@context"])

    if "eventList" in json_obj["epcisBody"]:
        event_list = json_obj["epcisBody"]["eventList"]
    else:
        # epcisBody may contain single event
        event_list = [json_obj["epcisBody"]["event"]]

    events = []

    # Correct JSON/XML data model mismatch
    for event in event_list:
        events.append(json_xml_model_mismatch_correction.deep_structure_correction(_json_to_py(event)))

    return ("EventList", "", events)
