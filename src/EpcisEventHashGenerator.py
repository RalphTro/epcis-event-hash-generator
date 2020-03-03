#!/usr/bin/python3
"""This is a prove of concept implementation of an algorithm to calculate a hash of EPCIS events. A small command line utility to calculate the hashes is provided for convenience.

.. module:: EpcisEventHashGenerator
   :synopsis: EPCIS event hash calculator.

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>, Sebastian Schmittner <schmittner@eecc.info>

Copyright 2019-2020 Ralph Troeger, Sebastian Schmittner

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""

import logging
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
import re
import hashlib

DIVISION_CHAR = ","

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
    ('bizTransactionList',[('bizTransaction', None)]),
    ('parentID', None),
    ('epcList', [('epc', None)]),
    ('inputEPCList', [('epc', None)]),
    ('childEPCs', [('epc', None)]),
    ('quantityList',[('quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ])]),
    ('childQuantityList',[('quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ])
    ]),
    ('inputQuantityList',[('quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ])]),
    ('outputEPCList',[('epc', None)]),
    ('outputQuantityList',[('quantityElement',
     [
         ('epcClass', None),
         ('quantity', None),
         ('uom', None)
     ])]),
    ('action', None),
    ('transformationID', None),
    ('bizStep', None),
    ('disposition', None),
    ('readPoint',[('id', None)]),
    ('bizLocation',[('id', None)]),
    ('bizTransactionList',[('bizTransaction', None)]),
    ('sourceList',[('source', None)]),
    ('destinationList',[('destination', None)]),
    ('sensorElementList',[('sensorElement',
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
     ])])#end sensorElement    
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
but NOT for top level elements.

"""

def readXmlFile(path):
    """Read XML file, remove useless extension tags and return parsed root element.

    """
    with open(path, 'r') as file:
        data = file.read()

    #TODO: this should not actually be needed:
    data = data.replace('<extension>', '').replace('</extension>', '').replace(
        '<baseExtension>', '').replace('</baseExtension>', '')
    logging.debug("removed extensions tags:\n%s", data)

    return ElementTree.fromstring(data)


def recurseThroughChildsInGivenOrderAndConcatText(root, childOrder):
    """Fetch all texts from root (if it is a simple element) or its
    children and concatenate the values in the given order. childOrder is
    expected to be a property order, see PROP_ORDER.

    """
    texts = ""
    for (childName, subChildOrder) in childOrder:
        # division char
        texts += DIVISION_CHAR
        #logging.debug("looking for child tag '%s' of root %s", childName, root)
        listOfValues = []
        for child in root.iterfind(childName):
            if subChildOrder:
                listOfValues.append(recurseThroughChildsInGivenOrderAndConcatText(child, subChildOrder))
            else:
                for text in child.itertext():
                    #logging.debug("Adding text '%s' from child %s", text, child)
                    listOfValues.append(text)
        #sort list of values of children with the same name to resolve issue 10
        logging.debug("sorting values %s", listOfValues)
        listOfValues.sort()
        logging.debug("sorted: %s", listOfValues)
        texts += "".join(listOfValues)

        #child name might also refer to an attribute
        texts += root.get(childName, "")        
                    
    return texts


def gatherElementsNotInChildOrder(root, childOrder):
    """
    Collects vendor extensions not covered by the defined child order. Consumes the root.
    """
    texts = ""
    
    for (childName, _) in childOrder:
        covered_children = root.findall(childName)
        logging.debug("Children '%s' covered by ordering: %s", childName, covered_children)
        for child in covered_children:
            root.remove(child)

    remaining_children = list(root)
    logging.debug("Remaining elements: %s", remaining_children)
    for child in remaining_children:
        texts += DIVISION_CHAR + child.tag.replace("{","").replace("}","#") + "="
        listOfValues = []
        for text in child.itertext():
            listOfValues.append(text)
        listOfValues.sort()
        texts += "".join(listOfValues)
      
    return texts


def computePreHashFromXmlFile(path):
    """Read EPCIS XML document and generate pre-hashe strings.

    """
    try:
        root = readXmlFile(path);
        logging.debug(root);
        events = list(root.find("*EventList"))
    except Exception as ex:
        logging.debug(ex)
        logging.error("'%s' does not contain an epcis xml document with EventList.", path)
        return []
    
    logging.debug("eventList=%s", events)
    
    preHashStringList = []
    for event in events:
        logging.debug("prehashing event:\n%s", event)
        try:
            preHashStringList.append(event.tag + ":" +
                recurseThroughChildsInGivenOrderAndConcatText(event, PROP_ORDER)[1:]
                + gatherElementsNotInChildOrder(event, PROP_ORDER)
            )
        except Exception as ex:
            logging.error("could not parse event:\n%s\n\nerror: %s", event, ex)
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
        else:
            raise ValueError("Unsupported Hashing Algorithm: " + hashString)
        
        hashValueList.append(hashString)

    return (hashValueList, preHashStringList)


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
    parser.add_argument("file", help="EPCIS file", nargs="+")
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
    parser.add_argument(
        "-b",
        "--batch",
        help="If given, write the new line separated list of hashes for each input file into a sibling output file with the same name + '.hashes' instead of stdout.",
        action="store_true")
    parser.add_argument(
        "-p",
        "--prehash",
        help="If given, also output the prehash string to stdout. Output to a .prehashes file, if combined with -b.",
        action="store_true")
    

    args = parser.parse_args()

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    #print("Log messages above level: {}".format(logger_cfg["level"]))

    if not args.file:
        logging.critical("File name required.")
        parser.print_help()
        sys.exit(1)
    else:
        logging.debug("reading from files: '{}'".format(args.file))

    for filename in args.file:
        # ACTUAL ALGORITHM CALL:
        (hashes, prehashes) = xmlEpcisHash(filename, args.algorithm)

        if args.batch:
            with open(filename+'.hashes', 'w') as outfile:
                outfile.write("\n".join(hashes)+"\n")
            if args.prehash:
                with open(filename+'.prehashes', 'w') as outfile:
                    outfile.write("\n".join(prehashes)+"\n")
        else:
            print("\n\nHashes of the events contained in '{}':\n{}".format(filename,hashes))
            if args.prehash:
                print("\nPre-hash strings:\n{}".format(prehashes))


# goto main if script is run as entrypoint
if __name__ == "__main__":
    main()
