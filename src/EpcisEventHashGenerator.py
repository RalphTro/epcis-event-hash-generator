#!/usr/bin/python3
"""This is a prove of concept implementation of an algorithm to calculate a hash of EPCIS events. A small command line utility to calculate the hashes is provided for convenience.

.. module:: EpcisEventHashGenerator
   :synopsis: EPCIS event hash calculator.

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>

Copyright 2019 Ralph Troeger

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""

import logging
import sys
import xml.etree.ElementTree as ET
from collections import Counter
import re
import hashlib


PROP_ORDER = [
    ('eventTime', None),
    ('eventTimeZoneOffset', None),
    ('eventID', None), #TODO: how to handle hash-id?
    ('errorDeclaration',
     [
         ('declarationTime', None),
         ('reason', None),
         ('correctiveEventIDs/correctiveEventID', None)
     ]),
    ('bizTransactionList/bizTransaction', None),
    ('parentID', None),
    ('epcList/epc', None),
    ('inputEPCList/epc', None),
    ('childEPCs/epc', None),
    ('quantityList/quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ]),
    ('childQuantityList/quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ]),
    ('inputQuantityList/quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ]),
    ('outputEPCList/epc', None),
    ('outputQuantityList/quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ]),
    ('action', None),
    ('transformationID', None),
    ('bizStep', None),
    ('disposition', None),
    ('readPoint/id', None),
    ('bizLocation/id', None),
    ('bizTransactionList/bizTransaction', None),
    ('sourceList/source', None),
    ('destinationList/destination', None),
    ('sensorElementList/sensorElement',
     [('sensorMetaData',
      [
          ('time', None),
          ('startTime',None),
          ('endTime',None),
          ('deviceID',None),
          ('deviceMetaData',None),
          ('rawData',None),
          ('dataProcessingMethod',None),
          ('bizRules', None)
      ]),#end sensorMetaData
      ('sensorReport',
       [
           ('type', None),
           ('deviceID', None),
           ('deviceMetaData', None),
           ('rawData', None),
           ('dataProcessingMethod', None),
           ('microorganism', None),
           ('chemicalSubstance', None),
           ('value', None),
           ('stringValue', None),
           ('booleanValue', None),
           ('hexBinaryValue', None),
           ('uriValue', None),
           ('minValue', None),
           ('maxValue', None),
           ('meanValue', None),
           ('sDev', None),
           ('percRank', None),
           ('percValue', None),
           ('uom', None),
       ])#end sensorReport
     ])#end sensorElement    
    ]
"""The property order data structure describes the ordering in which
to concatenate the values of the fields of EPCIS event. It is a list
of pairs. The first part of each pair is a string, naming the xml
element. If the element might have children whose order needs to be
defined, the second element is a property order for the children,
otherwise the second element is None.

For brevity, it is permissive to use e.g.
    ('readPoint/id', None)
instead of
    ('readPoint',[('id', None)])

"""

def readXmlFile(path):
    """Read XML file, remove useless extension tags and return parsed root element.

    """
    with open(path, 'r') as file:
        data = file.read()

    data = data.replace('<extension>', '').replace('</extension>', '').replace(
        '<baseExtension>', '').replace('</baseExtension>', '')
    logging.debug("removed extensions tags:\n%s", data)

    return ET.fromstring(data)


def recurseThroughChildsInGivenOrderAndConcatText(root, childOrder):
    """Fetch all texts from root (if it is a simple element) or its
    children and concatenate the values in the given order. childOrder is
    expected to be a property order, see PROP_ORDER.

    """
    texts = ""
    for (childName, subChildOrder) in childOrder:
        for child in root.iter(childName):
            if subChildOrder:
                texts += recurseThroughChildsInGivenOrderAndConcatText(child, subChildOrder)
            else:
                for text in child.itertext():
                    texts += text
    return texts


def computePreHashFromXmlFile(path):
    """Read EPCIS XML document and generate pre-hashe strings.

    """
    root = readXmlFile(path)

    # Extract all events that are part of eventList
    eventListElement = None
    for el in root.iter("EventList"):
        if eventListElement:
            logging.error("There should be at most one eventList tag!")
        eventListElement = el
    if eventListElement is None:
        logging.error("No eventList tag found")
        raise ValueError("No eventList tag found in " + path)

    logging.debug("eventListElement=%s", eventListElement)
    
    # Sort events by type
    # TODO: what about sorting among elements of the same type?
    eventList = []
    for e in eventListElement.iter("ObjectEvent"):
        eventList += e
    for e in eventListElement.iter("AggregationEvent"):
        eventList += e
    for e in eventListElement.iter("TransactionEvent"):
        eventList += e
    for e in eventListElement.iter("TransformationEvent"):
        eventList += e
    for e in eventListElement.iter("AssociationEvent"):
        eventList += e

    logging.debug("eventList=%s", eventList)
    
    preHashStringList = []
    for event in eventList:
        logging.debug("prehashing event:\n%s", event)
        try:
            preHashStringList += recurseThroughChildsInGivenOrderAndConcatText(event, PROP_ORDER)
        except Exception as e:
            logging.error("could not parse event:\n%s\n\nerror: %s", event, e)
            pass
        
        
    # To see/check concatenated value string before hash algorithm is performed:
    logging.debug("preHashStringList = {}".format(preHashStringList))

    return preHashStringList


def xmlEpcisHash(path, hashalg):
    """Read all EPCIS Events from the EPCIS XML document at path.
    Compute a normalized form (pre-hash string) for each event and
    return an array of the event hashes computed from the pre-hash by
    hashalg.
    """
    preHashStringList = computePreHashFromXmlFile(path)
    
    # Calculate hash values and prefix them according to RFC 6920
    hashValueList = []
    for preHashString in preHashStringList:
        if hashalg == 'sha256':
            hashString = 'ni:///sha-256;' + \
                hashlib.sha256(preHashString.encode('utf-8')).hexdigest()
        elif hashalg == 'sha3_256':
            hashString = 'ni:///sha3_256;' + \
                hashlib.sha3_256(preHashString.encode('utf-8')).hexdigest()
        elif hashalg == 'sha384':
            hashString = 'ni:///sha-384;' + \
                hashlib.sha384(preHashString.encode('utf-8')).hexdigest()
        elif hashalg == 'sha512':
            hashString = 'ni:///sha-512;' + \
                hashlib.sha512(preHashString.encode('utf-8')).hexdigest()
        hashValueList.append(hashString)

    return hashValueList


def main():
    """The main function reads the path to the xml file
    and optionally the hash algorithm from the command
    line arguments and calls the actual algorithm.
    """
    import argparse

    logger_cfg = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

    parser = argparse.ArgumentParser(
        description="Generate a canonical hash from an EPCIS Document.")
    parser.add_argument("-f", "--file", help="EPCIS file")
    parser.add_argument(
        "-a",
        "--algorithm",
        help="Hashing algorithm to use.",
        choices=["sha256", "sha3_256", "sha384", "sha512"],
        default="sha256")
    parser.add_argument(
        "-l",
        "--log",
        help="Set the log level. Default: INFO.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO")

    args = parser.parse_args()

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    #print("Log messages above level: {}".format(logger_cfg["level"]))

    if not args.file:
        logging.critical("File name required.")
        parser.print_help()
        sys.exit(1)
    else:
        logging.debug("reading from file: '{}'".format(args.file))

    print("Hashes of the events contained in '{}':\n{}".format(
        args.file, xmlEpcisHash(args.file, args.algorithm)))


# goto main if script is run as entrypoint
if __name__ == "__main__":
    main()
