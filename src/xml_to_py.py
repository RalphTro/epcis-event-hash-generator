"""Convert an EventList contained in an EPCIS 2.0 document in XML format into a simple python object.

A simple object here may be a
- string
- (ordered) tuple of simple object
- unordered list of simple objects

Mappings (dictionaries) are modeled as (unordered) lists of pairs.
Python lists are used although they are ordered, the order is to be ignored. (Sets are unsuitable since they enforce unique elements.)

For example
<obj>
  <a>
    <b>3</b>
    <b>5</b>
    <c e="f"><d>Hello</d><d>World</d></c>
  </a>
  <d>2</d>
</obj>

is converted to

obj = [("d","2"),("a",[("b","3"),("b","5"),("c",[("e","f"),("d","Hello"),("d","World")])])]

Caution: If an element has (attributes or children) and text, the text is ignored. Before/After text (e.g. <a> before_text <b>1</b></a>) is always ignored.


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


def read_epcis_document_xml(path):
    """Read XML file, remove useless EPCIS extension tags and return the parsed root of the ElementTree.
    """
    with open(path, 'r') as file:
        data = file.read()

    data = data.replace('<extension>', '').replace('</extension>', '').replace(
        '<baseExtension>', '').replace('</baseExtension>', '')
    logging.debug("removed extensions tags:\n%s", data)

    return ElementTree.fromstring(data)


def xml_to_py(root):
    """ Perform the conversion from ElementTree to a simple python object.
    """
    obj = []
    # add all XML Attributes
    obj += root.items()
        
    # Recurs through children    
    for child in root:
        obj.append((child.tag,  xml_to_py(child)))

    # If the element has neither attributes nor children, return the text
    if len(obj) == 0:
        return root.text

    # Sort lists to compensate for using ordered list to model unordered ones
    obj.sort()
    return obj


def event_list_from_epcis_document_xml(path):
    """Read EPCIS XML document and generate the event List in the form of a simple python object

    """
    try:
        root = read_epcis_document_xml(path);
        logging.debug("Reading %s yields %s = %s",path, root, list(root));
        eventList = root.find("*EventList")
        if not eventList:
            raise Exception("No EventList found")
    except Exception as ex:
        logging.debug(ex)
        logging.error("'%s' does not contain a valid EPCIS XML document with EventList.", path)
        return []

    obj = xml_to_py(eventList)

    logging.debug("Simple python object:\n%s", obj)
    
    return obj




    
