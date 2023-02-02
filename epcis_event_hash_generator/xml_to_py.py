"""Convert an EventList contained in an EPCIS 2.0 document in XML format into a simple python object
via the main method event_list_from_epcis_document_str.

A simple object here may be a
- string
- unordered list of simple objects
- pair of a string and a list of simple objects

Mappings (dictionaries) are modeled as (unordered) lists of pairs. Python lists are used although they are ordered,
the order is to be ignored. (Sets are unsuitable since they enforce unique elements.)

For example
<obj>
  <a>
    <b>3</b>
    <b>3</b>
    <b>5</b>
    <c e="f"><d>Hello</d><d x="y">World</d></c>
  </a>
  <d>2</d>
</obj>

is converted to

obj = [
        ("d","2",[]),
        ("a", "",
            [
                ("b","3",[]),
                ("b","3",[]),
                ("b","5",[]),
                ("c","",
                    [
                        ("e","f",[]),
                        ("d","Hello",[]),
                        ("d","World",
                            [
                                ("x","y",[])
                            ]
                        )
                    ]
                )
            ]
        )
    ]

Before/After text (e.g. <a> before_text <b>1</b></a>) is always ignored.


.. module:: xml_to_py

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
import xml.etree.ElementTree as ElementTree
from typing import Tuple

_expansions = {"gs1:": "https://gs1.org/voc/", "cbv:": "https://ref.gs1.org/cbv/"}


def _remove_extension_tags(data):
    """
    Remove useless EPCIS extension tags from a string
    """
    return data.replace('<extension>', '').replace('</extension>', '').replace(
        '<baseExtension>', '').replace('</baseExtension>', '')


def _expand_value_prefix(obj):
    """
    Expand namespaces used in string values, e.g.
    <sensorReport type="gs1:Temperature" value="26" uom="CEL" sDev="0.1"/>
    to
    <sensorReport type="https://gs1.org/voc/Temperature" value="26" uom="CEL" sDev="0.1"/>
    """

    # a special logic required to deal with nested tuple structure for elements
    # like sourceList, destinationList, bizTransactionList
    (restructured_obj, skip) = check_for_nested_tuples_with_type_attribute(obj)

    if skip:
        return restructured_obj
    else:
        for key, value in _expansions.items():
            if obj[1].startswith(key):
                obj = (obj[0], obj[1].replace(key, value), obj[2])

        new_kids = []
        for child in obj[2]:
            new_kids.append(_expand_value_prefix(child))
        return obj[0], obj[1], new_kids


def check_for_nested_tuples_with_type_attribute(obj):
    """
    Checks if type attribute value to be expanded in various nested tuple elements
    like source, destination, bizTranslation, etc.
    """
    skip = False
    restructured_obj = None
    altered = False

    for key, value in _expansions.items():
        if isinstance(obj, tuple) and len(obj) == 2:
            obj_as_list = list(obj)
            for index, child in enumerate(obj_as_list):
                if isinstance(child, tuple) and child[0] == 'type':
                    child_as_list = list(child)
                    skip = True
                    if str(child_as_list[1]).startswith(key):
                        altered = True
                        child_as_list[1] = str(child_as_list[1]).replace(key, value)
                        obj_as_list[index] = tuple(child_as_list)
            restructured_obj = tuple(obj_as_list)

    if altered:
        return restructured_obj, skip

    return obj, skip


def _xml_to_py(root, sort=True):
    """ Perform the conversion from ElementTree to a simple python object.
    """
    children = []

    # add all XML Attributes
    children += [(x, y, []) for (x, y) in root.items()]

    # Recurs through children
    for child in root:
        children.append(_xml_to_py(child))

    # Sort lists to compensate for using ordered list to model unordered ones
    if sort:
        children.sort()

    # ensure attributes & values of bizTransaction, source and destination are in expected order
    children_in_order = []
    for child in children:
        if child[0] == 'bizTransaction' or child[0] == 'source' or child[0] == 'destination':
            if isinstance(child[2], list):
                tuple_of_children = (child[2][0], (child[0], child[1], []))
                children_in_order.append(tuple_of_children)

    if children_in_order:
        children.clear()
        children += children_in_order

    text = ""
    if root.text:
        text = root.text.strip()
    obj = (root.tag, text, children)

    logging.debug("xml_to_py(%s) = %s", root, obj)
    return obj


def event_list_from_epcis_document_str(xmlStr: str) -> Tuple[str, str, list]:
    """
    Read EPCIS XML document and generate the event List in the form of a simple python object
    """
    try:
        data = _remove_extension_tags(xmlStr)

        root = ElementTree.fromstring(data)

        eventList = root.find("*EventList")
        if not eventList:
            raise ValueError("No EventList found")
    except (ValueError, OSError) as ex:
        logging.error(ex)
        logging.error("Input string does not contain a valid EPCIS XML document with EventList.")
        return ("", "", [])

    # sort=False => preserve document order of events
    obj = _xml_to_py(eventList, False)

    obj = _expand_value_prefix(obj)

    logging.debug("Simple python object:\n%s", obj)

    return obj
