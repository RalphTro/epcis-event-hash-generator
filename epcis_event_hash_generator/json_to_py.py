"""Convert an EventList contained in an EPCIS 2.0 document in JSON LD format into a simple python object.

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

SKIP_KEYS = ["isA", "#text"]

_namespaces = {}  # global dictionary gathered during parsing


def namespace_replace(key):
    """If the key contains a namespace (followed by ":"), replace it with
    the {naemspace_url} from the _namespaces dict.
    """
    splitted = key.split(":", 1)
    if len(splitted) > 1:
        return _namespaces[splitted[0]] + splitted[1]

    return key


def correct_xml_vs_js_structure_missmatch(py_obj):
    """
    Some of the object substructure in XML EPCIS is just not present in JSON or unsystematically renamed... oO
    """

    # readpoint and bizLocation have a nested id in XML but not in JSON
    if py_obj[0] == "readPoint" or py_obj[0] == "bizLocation":
        assert not py_obj[2]
        return py_obj[0], "", [("id", py_obj[1], [])]

    # bisTransaction, source and destination have a nested id in JSON but not in XML
    if py_obj[0] == "bizTransaction" or py_obj[0] == "source" or py_obj[0] == "destination":
        for element in [x for x in py_obj[2] if x[0] == py_obj[0]]:
            py_obj[2].remove(element)
            return py_obj[0], element[1], py_obj[2]

    # inconsistent child names / omissions
    if py_obj[0] == "inputEPC" or py_obj[0] == "outputEPC":
        return "epc", py_obj[1], py_obj[2]

    # quantity can be a quantityList child which should be called quantityElement (omitted in JSON) or the quantity
    # property of such an element... -.-
    if py_obj[0] == "inputQuantity" or py_obj[0] == "outputQuantity" or py_obj[0] == "childQuantity" or (py_obj[0] == "quantity" and len(py_obj[2]) > 0):
        return "quantityElement", py_obj[1], py_obj[2]

    if py_obj[0] == "inputQuantity" or py_obj[0] == "outputQuantity":
        return "quantityElement", py_obj[1], py_obj[2]

    return py_obj


def deep_structure_corretion(py_obj):
    """deep copy, applying xml_vs_js_structure_mismatch depth first"""

    corrected_children = []

    # particularly tricky case of structure mismatch: list of childEPCs VS childEPCs list of EPCs
    child_epcs = []
    for child in [element for element in py_obj[2] if element[0] == "childEPCs"]:
        child_epcs.append(("epc", child[1], []))

    if child_epcs:
        corrected_children.append(("childEPCs", "", child_epcs))

    # actual recursion
    for child in [element for element in py_obj[2] if not element[0] == "childEPCs"]:
        corrected_children.append(deep_structure_corretion(child))

    return correct_xml_vs_js_structure_missmatch((py_obj[0], py_obj[1], corrected_children))


def json_to_py(json_obj):
    """ Recursively convert a string/list/dict to a simple python object
    """
    global _namespaces

    py_obj = ("", "", [])

    if isinstance(json_obj, list):
        for child in json_obj:
            py_obj[2].append(json_to_py(child))
    elif isinstance(json_obj, dict):
        if "isA" in json_obj:
            py_obj = (json_obj["isA"], "", [])

        if "#text" in json_obj:
            py_obj = (py_obj[0], json_obj["#text"], py_obj[2])

        for (key, val) in [x for x in json_obj.items() if x[0] not in SKIP_KEYS]:
            if key.startswith("@xmlns"):
                _namespaces[key[7:]] = "{" + val + "}"
                logging.debug("Namespaces: %s", _namespaces)

                py_obj = (namespace_replace(py_obj[0]), py_obj[1], py_obj[2])
            else:
                # first find namespaces in child, then replace in key!
                child = json_to_py(val)

                key = namespace_replace(key)

                # Names of list elements (e.g. 'epc' elements of 'epsList') are omitted in current json ld form ->
                # restore
                if key.endswith("List"):
                    named_elements = []
                    for element in child[2]:
                        if not element[0]:
                            named_elements.append((key[:-4], element[1], element[2]))
                        else:
                            named_elements.append(element)
                    child = (key, child[1], named_elements)
                    py_obj[2].append(child)

                elif isinstance(val, list):
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


def event_list_from_epcis_document_json(path):
    """Read EPCIS JSON document and generate the event List in the form of a simple python object

    """
    with open(path, 'r') as file:
        data = file.read()

    json_obj = json.loads(data)

    event_list = json_obj["epcisBody"]["eventList"]
    events = []

    for event in event_list:
        events.append(deep_structure_corretion(json_to_py(event)))

    return ("EventList", "", events)