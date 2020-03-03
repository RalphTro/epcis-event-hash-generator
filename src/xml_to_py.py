"""Convert an EventList contained in an EPCIS 2.0 document in XML format into a python object.

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


def readXmlFile(path):
    """Read XML file, remove useless extension tags and return parsed root element.

    """
    with open(path, 'r') as file:
        data = file.read()

    data = data.replace('<extension>', '').replace('</extension>', '').replace(
        '<baseExtension>', '').replace('</baseExtension>', '')
    logging.debug("removed extensions tags:\n%s", data)

    return ElementTree.fromstring(data)

def xmlToPy(root):
    obj = []
    for pair in root.items():
        obj.append(pair)
    for child in root:
        obj.append((child.tag,  xmlToPy(child)))

    if len(obj) == 0:
        return root.text

    return obj

def eventListFromXmlFile(path):
    """Read EPCIS XML document and generate pre-hashe strings.

    """
    try:
        root = readXmlFile(path);
        logging.debug(root);
        eventList = root.find("*EventList")
        if not eventList:
            raise Exception("No EventList found")
    except Exception as ex:
        logging.debug(ex)
        logging.error("'%s' does not contain an epcis xml document with EventList.", path)
        return []

    return xmlToPy(e)




    
