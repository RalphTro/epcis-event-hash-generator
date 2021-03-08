""" Read EPCIS events from a JSON(-LD) or XML file and convert them into a simple puthon object
via the apropriate conversion module. See json_to_py / xml_to_py for details.

.. module:: events_from_file_reader

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

try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator import json_to_py
from epcis_event_hash_generator import xml_to_py


def _event_list_from_epcis_document_xml(path):
    """Read EPCIS XML document and generate the event List in the form of a simple python object

    """
    with open(path, 'r') as file:
        data = file.read()

    return xml_to_py.event_list_from_epcis_document_str(data)


def _event_list_from_epcis_document_json(path):
    """Read EPCIS JSON document and generate the event List in the form of a simple python object

    """
    with open(path, 'r') as file:
        data = file.read()

    return json_to_py.event_list_from_epcis_document_str(data)


def event_list_from_file(path, enforce=""):
    """Read all EPCIS Events from the EPCIS document at path.
    Return a python object representation of the contained events.

    Use enforce "XML" or "JSON" to ignore the file ending and parse the
    specified format.
    """

    if enforce == "XML" or path.lower().endswith(".xml"):
        return _event_list_from_epcis_document_xml(path)
    elif enforce == "JSON" or path.lower().endswith(".json") or path.lower().endswith(".jsonld"):
        return _event_list_from_epcis_document_json(path)
    else:
        logging.error("Filename '%s' ending not recognized.", path)
        return None
